FROM eclipse-temurin:17-jre-alpine

WORKDIR /home/app

COPY build/libs/docker-exercises-project-1.0-SNAPSHOT.jar app.jar

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

USER appuser

CMD [ "java", "-jar", "app.jar" ]