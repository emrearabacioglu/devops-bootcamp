# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Deploy Mosquitto message broker with ConfigMap and Secret Volume Types

### Demo Executed: Mount a ConfigMap and a Secret into Mosquitto

#### Created Mosquitto Deployment without any volumes
First ran Mosquitto without volumes to see the default config file:

    root@PC:~# cat mosquitto-without-volumes.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mosquitto
      labels:
        app: mosquitto
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mosquitto
      template:
        metadata:
          labels:
            app: mosquitto
        spec:
            containers:
              - name: mosquitto
                image: eclipse-mosquitto:2.0
                ports:
                  - containerPort: 1883

Applied it:

    root@PC:~# kubectl apply -f mosquitto-without-volumes.yaml
    deployment.apps/mosquitto created
    
    root@PC:~# kubectl get pod
    NAME                                 READY   STATUS    RESTARTS       AGE
    mongo-express-5747d566b9-wz2t6       1/1     Running   2 (3h39m ago)  61d
    mongodb-deployment-df5cd6568-5gp67   1/1     Running   2 (3h39m ago)  61d
    mosquitto-8bbb9c957-jjqq8            1/1     Running   0              11s

Default `mosquitto.conf` inside the container:

    root@PC:~# kubectl exec -it mosquitto-8bbb9c957-jjqq8 -- /bin/sh
    / # cd mosquitto/config/
    /mosquitto/config # cat mosquitto.conf
    # Config file for mosquitto
    #
    # See mosquitto.conf(5) for more information.
    #
    # Default values are shown, uncomment to change.
    ...
    /mosquitto/config # exit

Deleted this version:

    root@PC:~# kubectl delete -f mosquitto-without-volumes.yaml
    deployment.apps "mosquitto" deleted from default namespace

#### Created ConfigMap component to overwrite mosquitto.conf file
ConfigMap with a new `mosquitto.conf` (logging settings and listener port 9001):

    root@PC:~# cat config-file.yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
        name: mosquitto-config-file
    data:
        mosquitto.conf: |
            log_dest stdout
            log_type all
            log_timestamp true
            listener 9001
            
    root@PC:~# kubectl apply -f config-file.yaml
    configmap/mosquitto-config-file created

#### Created Secret component to add passwords file
Secret holding a file called `secret.file`:

    root@PC:~# cat secret-file.yaml
    apiVersion: v1
    kind: Secret
    metadata:
        name: mosquitto-secret-file
    type: Opaque
    data:
        secret.file: |
            VGVjaFdvcmxkMjAyMyEgLW4K
            
    root@PC:~# kubectl apply -f secret-file.yaml
    secret/mosquitto-secret-file created

Both the Secret and the ConfigMap are in the cluster:

    root@PC:~# kubectl get secret
    NAME                    TYPE     DATA   AGE
    mongodb-secret          Opaque   2      61d
    mosquitto-secret-file   Opaque   1      10s
    
    root@PC:~# kubectl get configmap
    NAME                    DATA   AGE
    kube-root-ca.crt        1      62d
    mongodb-configmap       1      61d
    mosquitto-config-file   1      24s

#### Adjusted Mosquitto Deployment to include volumes
Mounted the ConfigMap to `/mosquitto/config` and the Secret to `/mosquitto/secret` (read-only):

    root@PC:~# cat mosquitto.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: mosquitto
      labels:
        app: mosquitto
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: mosquitto
      template:
        metadata:
          labels:
            app: mosquitto
        spec:
            containers:
              - name: mosquitto
                image: eclipse-mosquitto:2.0
                ports:
                  - containerPort: 1883
                volumeMounts:
                  - name: mosquitto-config
                    mountPath: /mosquitto/config
                  - name: mosquitto-secret
                    mountPath: /mosquitto/secret
                    readOnly: true
            volumes:
              - name: mosquitto-config
                configMap:
                  name: mosquitto-config-file
              - name: mosquitto-secret
                secret:
                  secretName: mosquitto-secret-file

Applied it:

    root@PC:~# kubectl apply -f mosquitto.yaml
    deployment.apps/mosquitto created
    
    root@PC:~# kubectl get pod
    NAME                                 READY   STATUS    RESTARTS       AGE
    mongo-express-5747d566b9-wz2t6       1/1     Running   2 (3h54m ago)  61d
    mongodb-deployment-df5cd6568-5gp67   1/1     Running   2 (3h54m ago)  61d
    mosquitto-cf9f594cd-dr9wz            1/1     Running   0              12s

Inside the pod, the secret file is already decoded and `mosquitto.conf` is the one from the ConfigMap:

    root@PC:~# kubectl exec -it mosquitto-cf9f594cd-dr9wz -- /bin/sh
    / # cd mosquitto/secret/
    /mosquitto/secret # cat secret.file
    TechWorld2023! -n
    
    /mosquitto/secret # cd ../config/
    /mosquitto/config # cat mosquitto.conf
    log_dest stdout
    log_type all
    log_timestamp true
    listener 9001
    /mosquitto/config # exit
