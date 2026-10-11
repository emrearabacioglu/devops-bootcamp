# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Create Helm Chart for Microservices

### Demo Executed: One shared chart for the microservices and one for Redis

#### Created “microservices” Helm Chart
Created a chart called `microservice` that can be used for all the stateless services:

    root@PC:~/k8s/microservices# helm create microservice

`deployment.yaml` template. Name, replicas, image, port and env vars come from the values file:

    root@PC:~/k8s/microservices/helmchart/microservice/templates# cat deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: {{ .Values.appName }}
    spec:
      replicas: {{ .Values.appReplicas }}
      selector:
        matchLabels:
          app: {{ .Values.appName }}
      template:
        metadata:
          labels:
            app: {{ .Values.appName }}
        spec:
          containers:
          - name: {{ .Values.appName }}
            image: "{{ .Values.appImage }}:{{ .Values.appVersion }}"
            ports:
            - containerPort: {{ .Values.containerPort }}
            env:
            {{- range .Values.containerEnvVars }}
            - name: {{ .name }}
              value: {{ .value | quote }}
            {{- end }}

`service.yaml` template:

    root@PC:~/k8s/microservices/helmchart/microservice/templates# cat service.yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: {{ .Values.appName }}
    spec:
      type: {{ .Values.serviceType }}
      selector:
        app: {{ .Values.appName }}
      ports:
      - protocol: TCP
        port: {{ .Values.servicePort }}
        targetPort: {{ .Values.containerPort }}

#### Created values.yaml files for each microservice
Each service has its own values file, e.g. `email-service-values.yaml`:

    root@PC:~/k8s/microservices# cat email-service-values.yaml
    appName: emailservice
    appImage: gcr.io/google-samples/microservices-demo/emailservice
    appVersion: v0.8.0
    appReplicas: 2
    containerPort: 8080
    containerEnvVars:
    - name: PORT
      value: "8080"
    
    servicePort: 5000

Installed emailservice and recommendationservice on Minikube with the same chart and their own values files:

    root@PC:~/k8s/microservices# helm install -f email-service-values.yaml emailservice microservice
    NAME: emailservice
    LAST DEPLOYED: Fri Aug 21 15:13:00 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1
    
    root@PC:~/k8s/microservices# helm install -f values/recommendation-service-values.yaml recommendationservice microservice
    NAME: recommendationservice
    LAST DEPLOYED: Fri Aug 21 15:32:00 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1

Pods of both releases:

    root@PC:~/k8s/microservices# kubectl get pod
    NAME                                     READY   STATUS              RESTARTS      AGE
    emailservice-778b6cfbdd-27j5g            1/1     Running             0             19m
    emailservice-778b6cfbdd-9s5xg            1/1     Running             0             19m
    recommendationservice-5f556544d5-5zqbj   1/1     Running             0             11s
    recommendationservice-5f556544d5-wf7f4   0/1     ContainerCreating   0             12s

#### Created “redis” Helm Chart and values file for it
Redis got its own chart, with TCP probes, resource limits and an `emptyDir` volume:

    root@PC:~/k8s/microservices/charts# helm create redis

Rendered the templates with `helm template` to check the output:

    root@PC:~/k8s/microservices# helm template -f values/redis-values.yaml charts/redis
    ---
    # Source: redis/templates/deployment.yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: redis-cart
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: redis-cart
      template:
        metadata:
          labels:
            app: redis-cart
        spec:
          containers:
          - name: redis-cart
            image: "redis:alpine"
            ports:
            - containerPort: 6379
            livenessProbe:
              initialDelaySeconds: 5
              tcpSocket:
                port: 6379
              periodSeconds: 5
            readinessProbe:
              initialDelaySeconds: 5
              tcpSocket:
                port: 6379
              periodSeconds: 5
            resources:
              requests:
                cpu: 70m
                memory: 200Mi
              limits:
                cpu: 125m
                memory: 300Mi
            volumeMounts:
            - name: redis-data
              mountPath: /data
          volumes:
          - name: redis-data
            emptyDir: {}

Ran a dry run before the real install:

    root@PC:~/k8s/microservices# helm install --dry-run -f values/redis-values.yaml rediscart charts/redis
    NAME: rediscart
    LAST DEPLOYED: Fri Aug 21 15:48:51 2026
    NAMESPACE: default
    STATUS: pending-install
    REVISION: 1
    DESCRIPTION: Dry run complete

## Deploy Microservices with Helmfile

### Demo Executed: From helm install scripts to Helmfile

#### Deployed Microservices Application with "helm install"
`install.sh` runs one `helm install` per service with its values file:

    root@PC:~/k8s/microservices# cat install.sh
    helm install -f values/redis-values.yaml rediscart charts/redis
    
    helm install -f values/email-service-values.yaml emailservice charts/microservice
    helm install -f values/cart-service-values.yaml cartservice charts/microservice
    helm install -f values/currency-service-values.yaml currencyservice charts/microservice
    helm install -f values/payment-service-values.yaml paymentservice charts/microservice
    helm install -f values/recommendation-service-values.yaml recommendationservice charts/microservice
    helm install -f values/productcatalog-service-values.yaml productcatalogservice charts/microservice
    helm install -f values/shipping-service-values.yaml shippingservice charts/microservice
    helm install -f values/ad-service-values.yaml adservice charts/microservice
    helm install -f values/checkout-service-values.yaml checkoutservice charts/microservice
    helm install -f values/frontend-values.yaml frontendservice charts/microservice

Ran it, then removed all releases with `uninstall.sh`:

    root@PC:~/k8s/microservices# chmod u+x install.sh
    root@PC:~/k8s/microservices# ./install.sh
    NAME: rediscart
    LAST DEPLOYED: Fri Aug 21 15:57:39 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1
    DESCRIPTION: Install complete
    ...
    NAME: frontendservice
    LAST DEPLOYED: Fri Aug 21 15:57:42 2026
    NAMESPACE: default
    STATUS: deployed
    REVISION: 1
    
    root@PC:~/k8s/microservices# ./uninstall.sh
    release "rediscart" uninstalled
    release "emailservice" uninstalled
    ...
    release "frontendservice" uninstalled

#### Installed Helmfile
Downloaded the Linux release of Helmfile, extracted it and moved the binary to `/usr/local/bin`:

    root@PC:~/k8s/microservices# wget https://github.com/helmfile/helmfile/releases/download/v0.164.0/helmfile_0.164.0_linux_amd64.tar.gz
    
    root@PC:~/k8s/microservices# tar -zxvf helmfile_0.164.0_linux_amd64.tar.gz
    LICENSE
    README-zh_CN.md
    README.md
    helmfile
    
    root@PC:~/k8s/microservices# chmod +x helmfile
    root@PC:~/k8s/microservices# mv helmfile /usr/local/bin/
    
    root@PC:~/k8s/microservices# helmfile --version
    helmfile version 0.164.0

#### Created Helmfile
`helmfile.yaml` lists every release with its chart and values file. For `rediscart`, two values are overridden inline:

    root@PC:~/k8s/microservices# cat helmfile.yaml
    releases:
      - name: rediscart
        chart: charts/redis
        values:
          - values/redis-values.yaml
          - appReplicas: "1"
          - volumeName: "redis-cart-data"
    
      - name: emailservice
        chart: charts/microservice
        values:
          - values/email-service-values.yaml
    
      - name: cartservice
        chart: charts/microservice
        values:
          - values/cart-service-values.yaml
    
      - name: currencyservice
        chart: charts/microservice
        values:
          - values/currency-service-values.yaml
    
      - name: paymentservice
        chart: charts/microservice
        values:
          - values/payment-service-values.yaml
    
      - name: recommendationservice
        chart: charts/microservice
        values:
          - values/recommendation-service-values.yaml
    
      - name: productcatalogservice
        chart: charts/microservice
        values:
          - values/productcatalog-service-values.yaml
    
      - name: shippingservice
        chart: charts/microservice
        values:
          - values/shipping-service-values.yaml
    
      - name: adservice
        chart: charts/microservice
        values:
          - values/ad-service-values.yaml
    
      - name: checkoutservice
        chart: charts/microservice
        values:
          - values/checkout-service-values.yaml
    
      - name: frontendservice
        chart: charts/microservice
        values:
          - values/frontend-values.yaml

#### Deployed Helm Charts with Helmfile
Deployed all releases with `helmfile sync`:

    root@PC:~/k8s/microservices# helmfile sync
    Building dependency release=rediscart, chart=charts/redis
    Building dependency release=cartservice, chart=charts/microservice
    ...
    UPDATED RELEASES:
    NAME                    NAMESPACE   CHART                 VERSION   DURATION
    checkoutservice                     charts/microservice   0.1.0     2s
    recommendationservice               charts/microservice   0.1.0     2s
    ...

Checked the releases and the pods:

    root@PC:~/k8s/microservices# helmfile list
    NAME                    NAMESPACE       ENABLED INSTALLED       LABELS  CHART                   VERSION
    rediscart                               true    true                    charts/redis
    emailservice                            true    true                    charts/microservice
    ...
    
    root@PC:~/k8s/microservices# kubectl get pod
    NAME                                     READY   STATUS    RESTARTS   AGE
    adservice-5f8b8889c9-jzgmv               1/1     Running   0          46s
    cartservice-548cc667f7-8tfrw             1/1     Running   0          47s
    ...

Removed everything with `helmfile destroy`:

    root@PC:~/k8s/microservices# helmfile destroy
    Building dependency release=frontendservice, chart=charts/microservice
    ...
    Deleting frontendservice
    Deleting checkoutservice
    ...
    DELETED RELEASES:
    NAME                    NAMESPACE   DURATION
    recommendationservice               0s
    cartservice                         0s
    ...
