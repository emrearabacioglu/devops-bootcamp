# Java web app and MySQL on AWS, managed from a dedicated Ansible control node

**Technologies:** Ansible (`aws_ec2` dynamic inventory, Galaxy role `geerlingguy.mysql`), AWS (EC2, VPC, subnets, NAT Gateway, route tables, Security Groups, IAM role, SSM Parameter Store), MySQL, Java (Spring Boot), Amazon Linux 2023, Ubuntu 24.04

A classic two-tier setup on AWS: a Java web application on one server and its MySQL database on another. The database server has no public IP and sits in a private subnet, so it can only be reached from inside the VPC. Everything is provisioned and configured with Ansible from a dedicated control node in the same VPC. The local machine only creates and prepares that control node. The web and database playbooks run on the control node, because it is the only Ansible host that can reach the database's private IP.

## How it works

```
Local machine
  ├─ provision-ansible-server.yaml   key pair, SG (22 from my IP), IAM role, EC2 ansible-server
  ├─ configure-ansible-server.yaml   Python 3.12 + Ansible + boto3, SSH key, control-node/ folder, mysql role
  └─ terminate-control-node.yaml     removes control node resources(run after destroy-resources.yaml)
                    │
                    ▼
Ansible control node (ansible-server, AWS access through its IAM role)
  ├─ provision-webserver-db.yaml     private subnet, NAT Gateway, route table, SGs, web + db servers
  ├─ configure-webserver-db.yaml     MySQL on db-server, Java app on web-server
  └─ destroy-resources.yaml          removes everything above
```

Network layout in the default VPC (`172.31.0.0/16`):

```
public subnet (default)                       private subnet 172.31.48.0/20
  ├─ ansible-server  (SG: 22 from my IP)        └─ db-server  (no public IP)
  ├─ web-server      (SG: 8080 from anywhere,        SG: 22 from VPC, 3306 from web-sg only
  │                   22 from VPC)                   route: 0.0.0.0/0 → NAT Gateway
  └─ NAT Gateway + Elastic IP  ◄──────────────────── outbound only (apt, MySQL packages)
     route: 0.0.0.0/0 → Internet Gateway
```

| File                                                                                                | What it does                                                                                                                                                                                                              |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `provision-ansible-server.yaml`                                                                   | Imports the SSH key as a key pair, creates the control node's security group and an IAM role (EC2 full access, SSM read), launches the control node with that role.                                                       |
| `configure-ansible-server.yaml`                                                                   | Installs Python 3.12, then Ansible, boto3 and botocore with pip for `ec2-user`. Copies the SSH private key and the `control-node/` folder, installs the `geerlingguy.mysql` role.                                    |
| `terminate-control-node.yaml`                                                                     | Deletes the control node, its security group, the IAM role with its instance profile, and the key pair.                                                                                                                   |
| `inventory_aws_ec2.yaml`, `ansible.cfg`, `group_vars/`                                        | Local setup: finds the control node by tags and connects to its public address.                                                                                                                                           |
| `control-node/provision-webserver-db.yaml`                                                        | Reads the default VPC and its default subnets, creates the private subnet, NAT Gateway, route table and both security groups, then launches the web server in a public subnet and the database server in the private one. |
| `control-node/configure-webserver-db.yaml`                                                        | Database: `geerlingguy.mysql` with a database and an app user. Web: Java 17, app user, stops an old instance of the app, copies the jar and starts it with the database settings.                                        |
| `control-node/destroy-resources.yaml`                                                             | Deletes the web and database servers, the NAT Gateway with its Elastic IP, the route table, the private subnet and both security groups.                                                                                  |
| `control-node/inventory_aws_ec2.yaml`, `control-node/ansible.cfg`, `control-node/group_vars/` | Control node setup: connects to every host by its private IP and uses the key in `/home/ec2-user/.ssh`.                                                                                                                  |
| `control-node/build-tools-exercises-1.0-SNAPSHOT.jar`                                             | The Spring Boot application. It reads its database settings from `DB_SERVER`, `DB_NAME`, `DB_USER` and `DB_PWD`.                                                                                                   |
| `test-all.sh`, `test.log`                                                                       | End-to-end test run and its output.                                                                                                                                                                                       |

### Decisions

- **AWS access through an IAM role.** The control node gets its AWS permissions from an IAM role attached as an instance profile. No access keys are copied to the server.
- **Private subnet with a NAT Gateway.** The database server needs internet access to install MySQL but must not be reachable from outside. Its subnet routes outbound traffic through a NAT Gateway in a public subnet and has no route to the Internet Gateway.
- **Database open only to the web server.** Port 3306 on `db-sg` accepts traffic only from instances in `web-sg`, not from a whole IP range. SSH on both servers is limited to the VPC, so only the control node can connect.
- **Two inventories.** Locally, hosts are reached by their public address. On the control node, `ansible_host` is set to `private_ip_address`, because the database server has no public address.
- **Safe re-runs.** Only the VPC's default subnets are used as public subnets (`default-for-az` filter), so the private subnet is never picked by mistake. The NAT Gateway uses `if_exist_do_not_create`, the route table is found by its tags, and instances use `exact_count: 1` with tag filters.
- **MySQL from a Galaxy role.** `geerlingguy.mysql` installs and configures MySQL, creates the database and a user that may connect from other hosts (`host: "%"`). The role supports Ubuntu but not Amazon Linux 2023, so the database server runs Ubuntu.
- **App started in the background and checked by port.** The app is started with `nohup` so it keeps running after the SSH session ends, with its output in `app.log`. `wait_for` on port 8080 makes the play fail if the app crashes on startup, for example when it can't reach the database.
- **Destroy in two steps and in order.** Resources created on the control node are deleted there first: instances, NAT Gateway (releasing its Elastic IP), route table, subnet, then `db-sg` before `web-sg` because it references it. The control node, its IAM role and the key pair are deleted last from the local machine.

## Requirements

Local machine:

- Ansible with the `amazon.aws` and `community.general` collections, and `boto3` / `botocore` in the same Python environment
- AWS credentials in `~/.aws/credentials` with EC2, IAM and SSM read permissions
- SSH key pair at `/root/.ssh/id_rsa` and `/root/.ssh/id_rsa.pub`
- AWS CLI and `curl` (only for `test-all.sh`)

## Usage

On the local machine, in this folder:

```bash
ansible-playbook provision-ansible-server.yaml
ansible-playbook configure-ansible-server.yaml
ssh ec2-user@<ansible-server-public-ip>
```

On the control node:

```bash
cd ~/control-node
ansible-playbook provision-webserver-db.yaml
ansible-playbook configure-webserver-db.yaml
```

The app is then at `http://<web-server-public-ip>:8080`.

To delete everything, first on the control node, then locally:

```bash
ansible-playbook destroy-resources.yaml           # on the control node
ansible-playbook terminate-control-node.yaml      # on the local machine
```

## Testing

`test-all.sh` runs the whole flow from the local machine and stops at the first error. It creates and configures the control node, then runs the control node's playbooks on it over SSH, so they still execute inside the VPC. After that it checks the app from the internet with `curl`, waits for a key press (or 10 minutes), and destroys everything. If a step fails, it prints the commands needed to clean up.

```bash
bash test-all.sh 2>&1 | tee test.log
```

Results from [`test.log`](./test.log):

- The control node's inventory first showed only itself, which confirmed that the IAM role and the dynamic inventory work. After provisioning it showed `web-server` and `db-server` in their own groups.
- The database server appeared only under its private DNS name (`ip-172-31-59-194...`), with no public address.
- MySQL and the app were configured with `failed=0` on both servers.
- The app answered `HTTP 200` on `http://<web-server-public-ip>:8080` from the internet.
- Both destroy playbooks finished with `failed=0`.
