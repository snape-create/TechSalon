FROM ubuntu
WORKDIR /usr/src/cpp
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install -y build-essential
RUN echo "#include <iostream>" > main.cpp
RUN echo "int main() {" >> main.cpp
RUN echo "\tstd::cout << \"Hello world!\" << std::endl;" >> main.cpp
RUN echo "\treturn 0;" >> main.cpp
RUN echo "}" >> main.cpp
RUN g++ main.cpp -o main
CMD ["./main"]