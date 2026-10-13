# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Configure Dynamic Inventory

### Demo Executed: Use the aws_ec2 Inventory Plugin Instead of a Static Hosts File

#### Infrastructure
The EC2 instances are created with Terraform in the default VPC, in a few steps:

* First 3 servers were created, and the playbook configured all of them through the dynamic inventory.
* A 4th server was added. The next `ansible-inventory` run listed it automatically, without editing any file.
* Finally the servers were tagged as 2 `dev-server` and 2 `prod-server`, so they can be grouped by tag.

#### Inventory Plugin Configuration
The `aws_ec2` plugin (from the `amazon.aws` collection, uses `boto3`) queries AWS for the running instances. The config file name must end with `aws_ec2.yaml`.

* `keyed_groups` creates groups dynamically: one group per Name tag value (`tag_Name_...`) and one per instance type (`instance_type_...`).
* In the default VPC the instances have public DNS names, so the plugin uses them as host names.

`inventory_aws_ec2.yaml`:

```yaml
    ---
    plugin : aws_ec2
    regions:
      - eu-central-1

    keyed_groups:
      - key: tags
        prefix: tag

      - key: instance_type
        prefix: instance_type
```

`ansible.cfg` uses the plugin file as the default inventory and sets the SSH user and key for all servers, so no `-i` or connection parameters are needed:

```properties
    [defaults]
    host_key_checking = False
    inventory = inventory_aws_ec2.yaml

    enable_plugins = aws_ec2

    remote_user = ec2-user
    private_key_file = /root/.ssh/id_rsa
```

#### Dynamic Groups
`ansible-inventory --graph` shows the groups created from the Name tags and the instance type:

```bash
    (.venv) root@PC:~/modules/ansible/05-dynamic-inventory (main)# ansible-inventory -i inventory_aws_ec2.yaml --graph
    @all:
      |--@ungrouped:
      |--@aws_ec2:
      |  |--ec2-52-57-37-126.eu-central-1.compute.amazonaws.com
      |  |--ec2-35-159-49-8.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-183-143-52.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-181-5-198.eu-central-1.compute.amazonaws.com
      |--@tag_Name_prod_server:
      |  |--ec2-52-57-37-126.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-183-143-52.eu-central-1.compute.amazonaws.com
      |--@instance_type_t3_small:
      |  |--ec2-52-57-37-126.eu-central-1.compute.amazonaws.com
      |  |--ec2-35-159-49-8.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-183-143-52.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-181-5-198.eu-central-1.compute.amazonaws.com
      |--@tag_Name_dev_server:
      |  |--ec2-35-159-49-8.eu-central-1.compute.amazonaws.com
      |  |--ec2-63-181-5-198.eu-central-1.compute.amazonaws.com
```

#### Playbook
The playbook is the same as in the Ansible Integration in Terraform project. Only the target changed: all plays use the dynamic group `tag_Name_dev_server`, so only the dev servers are configured.

```yaml
    ---
    - name: Wait SSH connection
      hosts: tag_Name_dev_server
      gather_facts: False
      tasks:
        - name: Wait SSH connection
          wait_for:
            port: 22
            delay: 10
            timeout: 120
            search_regex: OpenSSH
            host: '{{ (ansible_ssh_host|default(ansible_host))|default(inventory_hostname) }}'
          vars:
            ansible_connection: local
            ansible_python_interpreter: /usr/bin/python3

    - name: Install Docker
      hosts: tag_Name_dev_server
      become: yes
      ...

    - name: Start docker containers
      hosts: tag_Name_dev_server
      become: yes
      become_user: dockeruser
      vars_files: project-vars
      ...
```

#### Execution
Only the 2 dev servers are targeted; the prod servers are skipped:

```bash
    (.venv) root@PC:~/modules/ansible/05-dynamic-inventory (main)# ansible-playbook deploy-docker-dynamic.yaml

    PLAY [Wait SSH connection] ****

    TASK [Wait SSH connection] ****
    ok: [ec2-35-159-49-8.eu-central-1.compute.amazonaws.com]
    ok: [ec2-63-181-5-198.eu-central-1.compute.amazonaws.com]

    PLAY [Install Docker] ****

    TASK [Gathering Facts] ****
    ok: [ec2-35-159-49-8.eu-central-1.compute.amazonaws.com]
    ok: [ec2-63-181-5-198.eu-central-1.compute.amazonaws.com]

    TASK [Install Docker] ****
    ok: [ec2-35-159-49-8.eu-central-1.compute.amazonaws.com]
    ok: [ec2-63-181-5-198.eu-central-1.compute.amazonaws.com]
    ...
    PLAY [Start docker containers] ****
    ...
    TASK [Start containers] ****
    changed: [ec2-63-181-5-198.eu-central-1.compute.amazonaws.com]
    changed: [ec2-35-159-49-8.eu-central-1.compute.amazonaws.com]

    PLAY RECAP ****
    ec2-35-159-49-8.eu-central-1.compute.amazonaws.com : ok=14   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
    ec2-63-181-5-198.eu-central-1.compute.amazonaws.com : ok=14   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
