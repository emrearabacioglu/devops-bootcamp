FROM eclipse-temurin:17-jre
EXPOSE 8080 8081
RUN mkdir /opt/app
COPY build/libs/*.jar /opt/app/java-app.jar
WORKDIR /opt/app
CMD ["java", "-jar", "java-app.jar"]
