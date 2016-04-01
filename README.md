## Overview

Apache Flink is a ...
... Learn more
at [flink.apache.org](http://flink.apache.org).

This charm supports running Flink in two execution modes:

 * Local Mode: Flink runs using your local host and file system. Specify local
   mode using ...
 * Mapreduce Mode: Flink runs using a Hadoop cluster and HDFS. This is the default
   mode; 
   ........


## Usage
This charm leverages our pluggable Hadoop model with the `hadoop-plugin`
interface. This means that you will need to deploy a base Apache Hadoop cluster
to run Flink. The suggested deployment method is to use the
...................................
bundle. This will deploy the Apache Hadoop platform with a single Apache Flink
unit that communicates with the cluster by relating to the
`apache-hadoop-plugin` subordinate charm:

    juju quickstart ...

Alternatively, you may manually deploy the recommended environment as follows:

    juju deploy apache-hadoop-namenode namenode
    juju deploy apache-hadoop-resourcemanager resourcemanager
    juju deploy apache-hadoop-slave slave
    juju deploy apache-hadoop-plugin plugin
    juju deploy apache-flink flink

    juju add-relation resourcemanager namenode
    juju add-relation resourcemanager slave
    juju add-relation namenode slave
    juju add-relation plugin resourcemanager
    juju add-relation plugin namenode
    juju add-relation flink plugin

### Local Mode
Once deployment is complete, run Flink in local mode on the Flink unit with the
following:

    juju ssh flink/0
    ...

### MapReduce Mode
MapReduce mode is the default for Flink. To run in this mode, ssh to the Flink unit
and run flink as follows:

    juju ssh flink/0
    flink


## Testing the deployment

### Smoke test Local Mode
SSH to the Flink unit and run flink as follows:

    juju ssh flink/0
    ......
        
### Smoke test MapReduce Mode
SSH to the Flink unit and test in MapReduce mode as follows:

    juju ssh flink/0
    hdfs dfs -mkdir /flink/
    wget -O hamlet.txt http://www.gutenberg.org/cache/epub/1787/pg1787.txt
    hdfs dfs -put hamlet.txt /flink/
    flink run ./examples/WordCount.jar hdfs:///flink/hamlet.txt hdfs:///flink/wordcount-result.txt

## Contact Information

- bigdata@lists.ubuntu.com

