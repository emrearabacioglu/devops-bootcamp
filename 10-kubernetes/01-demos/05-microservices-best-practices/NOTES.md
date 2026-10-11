# Study Notes

My step-by-step notes for this demo, with the commands and terminal output from when I did it.

## Deploy Microservices application in Kubernetes with Production & Security Best Practices

### Demo Executed: Online shop microservices on LKE

#### Cluster Provisioning and Authentication
Created a 3-node cluster on LKE. Made the kubeconfig file read-only for my user, exported it and checked the nodes:

    root@PC:~/microservices# chmod 400 online-shop-microservices-kubeconfig.yaml
    root@PC:~/microservices# ls -l online-shop-microservices-kubeconfig.yaml
    -r-------- 1 root root 2825 Aug 20 22:44 online-shop-microservices-kubeconfig.yaml
    
    root@PC:~/microservices# export KUBECONFIG=~/microservices/online-shop-microservices-kubeconfig.yaml
    
    root@PC:~/microservices# kubectl get node
    NAME                     STATUS   ROLES    AGE     VERSION
    lke645983-950801-8j6d4   Ready    <none>   3m26s   v1.36.2
    lke645983-950801-8prw6   Ready    <none>   3m28s   v1.36.2
    lke645983-950801-bv6kj   Ready    <none>   3m31s   v1.36.2

#### Config File with Best Practices
One `config.yaml` with a Deployment and a Service for each of the 11 microservices. What's in it:
*   **Fixed image versions:** every image has a tag (`v0.8.0`, `redis:alpine`), no `latest`.
*   **Replicas:** most Deployments have `replicas: 2`.
*   **Health checks:** `livenessProbe` and `readinessProbe` with gRPC, TCP or HTTP.
*   **Resources:** CPU and memory `requests` and `limits`.
*   **No NodePort:** backend services are `ClusterIP`, only the frontend is a `LoadBalancer`.

<img width="2993" height="1396" alt="image" src="https://github.com/user-attachments/assets/7e178072-2ac3-49ca-8cdd-fca54c96cdb6" />

`config.yaml`:

```
    root@PC:~/microservices# touch config.yaml
    root@PC:~/microservices# cat config.yaml
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: emailservice
    spec:
      selector:
        matchLabels:
          app: emailservice
      template:
        metadata:
          labels:
            app: emailservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/emailservice:v0.8.0
            ports:
            - containerPort: 8080
            env:
            - name: PORT
              value: "8080"
            livenessProbe:
              grpc:
                port: 8080
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 8080
              periodSeconds: 5
            resources:
              requests:
                cpu: 100m
                memory: 64Mi
              limits:
                cpu: 200m
                memory: 128Mi
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: emailservice
    spec:
      type: ClusterIP
      selector:
        app: emailservice
      ports:
      - protocol: TCP
        port: 5000
        targetPort: 8080
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: recommendationservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: recommendationservice
      template:
        metadata:
          labels:
            app: recommendationservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/recommendationservice:v0.8.0
            ports:
            - containerPort: 8080
            env:
            - name: PORT
              value: "8080"
            - name: PRODUCT_CATALOG_SERVICE_ADDR
              value: "productcatalogservice:3550"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 8080
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 8080
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: recommendationservice
    spec:
      type: ClusterIP
      selector:
        app: recommendationservice
      ports:
      - protocol: TCP
        port: 8080
        targetPort: 8080
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: productcatalogservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: productcatalogservice
      template:
        metadata:
          labels:
            app: productcatalogservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/productcatalogservice:v0.8.0
            ports:
            - containerPort: 3550
            env:
            - name: PORT
              value: "3550"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 3550
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 3550
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: productcatalogservice
    spec:
      type: ClusterIP
      selector:
        app: productcatalogservice
      ports:
      - protocol: TCP
        port: 3550
        targetPort: 3550
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: paymentservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: paymentservice
      template:
        metadata:
          labels:
            app: paymentservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/paymentservice:v0.8.0
            ports:
            - containerPort: 50051
            env:
            - name: PORT
              value: "50051"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 50051
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 50051
              periodSeconds: 5
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: paymentservice
    spec:
      type: ClusterIP
      selector:
        app: paymentservice
      ports:
      - protocol: TCP
        port: 50051
        targetPort: 50051
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: currencyservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: currencyservice
      template:
        metadata:
          labels:
            app: currencyservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/currencyservice:v0.8.0
            ports:
            - containerPort: 7000
            env:
            - name: PORT
              value: "7000"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 7000
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 7000
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: currencyservice
    spec:
      type: ClusterIP
      selector:
        app: currencyservice
      ports:
      - protocol: TCP
        port: 7000
        targetPort: 7000
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: shippingservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: shippingservice
      template:
        metadata:
          labels:
            app: shippingservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/shippingservice:v0.8.0
            ports:
            - containerPort: 50051
            env:
            - name: PORT
              value: "50051"
            livenessProbe:
              grpc:
                port: 50051
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 50051
              periodSeconds: 5
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: shippingservice
    spec:
      type: ClusterIP
      selector:
        app: shippingservice
      ports:
      - protocol: TCP
        port: 50051
        targetPort: 50051
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: adservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: adservice
      template:
        metadata:
          labels:
            app: adservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/adservice:v0.8.0
            ports:
            - containerPort: 9555
            env:
            - name: PORT
              value: "9555"
            livenessProbe:
              grpc:
                port: 9555
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 9555
              periodSeconds: 5
            resources:
              requests:
                cpu: 200m
                memory: 180Mi
              limits:
                cpu: 300m
                memory: 300Mi
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: adservice
    spec:
      type: ClusterIP
      selector:
        app: adservice
      ports:
      - protocol: TCP
        port: 9555
        targetPort: 9555
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: cartservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: cartservice
      template:
        metadata:
          labels:
            app: cartservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/cartservice:v0.8.0
            ports:
            - containerPort: 7070
            env:
            - name: PORT
              value: "7070"
            - name: REDIS_ADDR
              value: "redis-cart:6379"
            - name: DISABLE_PROFILER
              value: "1"
            livenessProbe:
              grpc:
                port: 7070
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 7070
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: cartservice
    spec:
      type: ClusterIP
      selector:
        app: cartservice
      ports:
      - protocol: TCP
        port: 7070
        targetPort: 7070
    
    ---
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
          - name: redis
            image: redis:alpine
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
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: redis-cart
    spec:
      type: ClusterIP
      selector:
        app: redis-cart
      ports:
      - protocol: TCP
        port: 6379
        targetPort: 6379
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: checkoutservice
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: checkoutservice
      template:
        metadata:
          labels:
            app: checkoutservice
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/checkoutservice:v0.8.0
            ports:
            - containerPort: 5050
            env:
            - name: PORT
              value: "5050"
            - name: PRODUCT_CATALOG_SERVICE_ADDR
              value: "productcatalogservice:3550"
            - name: SHIPPING_SERVICE_ADDR
              value: "shippingservice:50051"
            - name: PAYMENT_SERVICE_ADDR
              value: "paymentservice:50051"
            - name: EMAIL_SERVICE_ADDR
              value: "emailservice:5000"
            - name: CURRENCY_SERVICE_ADDR
              value: "currencyservice:7000"
            - name: CART_SERVICE_ADDR
              value: "cartservice:7070"
            livenessProbe:
              grpc:
                port: 5050
              periodSeconds: 5
            readinessProbe:
              grpc:
                port: 5050
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: checkoutservice
    spec:
      type: ClusterIP
      selector:
        app: checkoutservice
      ports:
      - protocol: TCP
        port: 5050
        targetPort: 5050
    
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: frontend
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: frontend
      template:
        metadata:
          labels:
            app: frontend
        spec:
          containers:
          - name: service
            image: gcr.io/google-samples/microservices-demo/frontend:v0.8.0
            ports:
            - containerPort: 8080
            env:
            - name: PORT
              value: "8080"
            - name: PRODUCT_CATALOG_SERVICE_ADDR
              value: "productcatalogservice:3550"
            - name: CURRENCY_SERVICE_ADDR
              value: "currencyservice:7000"
            - name: CART_SERVICE_ADDR
              value: "cartservice:7070"
            - name: RECOMMENDATION_SERVICE_ADDR
              value: "recommendationservice:8080"
            - name: SHIPPING_SERVICE_ADDR
              value: "shippingservice:50051"
            - name: CHECKOUT_SERVICE_ADDR
              value: "checkoutservice:5050"
            - name: AD_SERVICE_ADDR
              value: "adservice:9555"
            livenessProbe:
              httpGet:
                path: "/_healthz"
                port: 8080
              periodSeconds: 5
            readinessProbe:
              httpGet:
                path: "/_healthz"
                port: 8080
              periodSeconds: 5
    
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: frontend
    spec:
      type: LoadBalancer
      selector:
        app: frontend
      ports:
      - protocol: TCP
        port: 80
        targetPort: 8080
```

#### Namespace Isolation and Microservices Deployment
Created a `microservices` namespace and applied the file there. All pods came up:

```
    root@PC:~/microservices# kubectl create ns microservices
    namespace/microservices created
    
    root@PC:~/microservices# kubectl apply -f config.yaml -n microservices
    deployment.apps/emailservice created
    service/emailservice created
    deployment.apps/recommendationservice created
    service/recommendationservice created
    deployment.apps/productcatalogservice created
    service/productcatalogservice created
    ...
    deployment.apps/frontend created
    service/frontend created
    
    root@PC:~/microservices# kubectl get pod -n microservices
    NAME                                     READY   STATUS    RESTARTS      AGE
    adservice-7dcbd647b4-dgpsh               1/1     Running   0             61s
    cartservice-75cd7bb67b-65z46             1/1     Running   0             60s
    checkoutservice-7879b466b9-v9bjq         1/1     Running   0             60s
    currencyservice-7bdfdf6dc7-j66tt         1/1     Running   0             61s
    emailservice-65f667bb5b-pmx67            0/1     Running   1 (11s ago)   63s
    frontend-5dcd6f968c-74nmb                1/1     Running   0             59s
    paymentservice-64c7d98d5-52qhx           1/1     Running   0             62s
    productcatalogservice-576696c58c-g5d6t   1/1     Running   0             62s
    recommendationservice-57cfddb6c9-8ft7w   1/1     Running   0             62s
    redis-cart-6448465667-kfjqh              1/1     Running   0             60s
    shippingservice-c9848967f-jtc6x          1/1     Running   0             61s
```

#### Exposed External Traffic (Accessed Online Shop)
Only the frontend has an external IP (`139.162.172.76`), the other services are ClusterIP:

```
    root@PC:~/microservices# kubectl get svc -n microservices
    NAME                    TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)        AGE
    adservice               ClusterIP      10.128.224.167   <none>           9555/TCP       85s
    cartservice             ClusterIP      10.128.132.55    <none>           7070/TCP       85s
    checkoutservice         ClusterIP      10.128.210.210   <none>           5050/TCP       85s
    currencyservice         ClusterIP      10.128.253.70    <none>           7000/TCP       86s
    emailservice            ClusterIP      10.128.15.127    <none>           5000/TCP       87s
    frontend                LoadBalancer   10.128.45.166    139.162.172.76   80:32023/TCP   84s
    paymentservice          ClusterIP      10.128.229.163   <none>           50051/TCP      86s
    productcatalogservice   ClusterIP      10.128.161.225   <none>           3550/TCP       87s
    recommendationservice   ClusterIP      10.128.254.90    <none>           8080/TCP       87s
    redis-cart              ClusterIP      10.128.66.178    <none>           6379/TCP       85s
    shippingservice         ClusterIP      10.128.186.29    <none>           50051/TCP      86s
```

#### Verified External Traffic (Accessed Online Shop via Browser)
The online shop opened in the browser on the frontend's external IP:

<img width="1890" height="968" alt="image" src="https://github.com/user-attachments/assets/15d8a2fe-810a-4f14-b815-8ad417e042a1" />
