##**Create kms docker stack with dependencies**

## 1. purpose:
build a dock stack (bases on docker swarm) env inlcuing kms,mongo,elasticsearch,kibana,monstache(sync data from mongodb to elasticsearch)

## 2. Steps 

1. docker swarm env ,here only use 1 node, you can change it to multiple nodes
   ```
   docker swarm init
   ```
2. create a docker stack(nameL: kms) based on kms-docker-stack.yml
   ```
   docker stack deploy -c kms-docker-stack.yml kms 
   ```