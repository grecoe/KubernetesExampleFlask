# KubernetesExampleFlask - Source
<sup> By Dan Grecoe a Microsoft Engineer </sup>

This directory contains the files and scripts you'll need for different steps along the way in this journey. You will, of course, need to perform other tasks on your own. So, what are the files?

| File Name | Purpose | 
|------------------|--------------------|
| app.py | A VERY simple Flask Application written in Python. This is what will be contained in the Docker container. |
| Dockerfile | This is the file required by Docker to create the container.|
| requirements.txt | Consumed by Docker and called out in the Dockerfile to identify requirements for the container. |
| deployimage.yaml | This file will be used to deploy our container to AKS.|
| giveaccessrights.ps1 | Script that will be run to allow AKS to pull images from the ACR.|

# Getting set up
Now, you could do some of these steps on your own Ubuntu machine, you do NOT need to have an Azure Data Science Virtual Machine, though it makes it simpler. 

Give that, the instructions I'm going to provde assume that you will create a single Ubuntu DSVM.

## Create Azure Resources

```
NOTE: These steps also assume some familiarity with Azure Portal. 
```

### Azure Resource Group
Go to [AzurePortal](http://portal.azure.com) and select your subscription. 
- Click Resource groups
- Click Add
- Remember the region

### Azure Container Service (ACR)
On the [AzurePortal](http://portal.azure.com), find the resource group you made. When you open it click Add
- Search for Container registry
- Click on the resulting <b>Container registry</b> in the list.
- Click create
- It's fine to keep all defaults EXCEPT, for <b>Admin user</b>, change this setting to enabled. It will allow us to log into the container registry with the registry name and a key. 
- Just be sure that the registry is being created in the resource group created earlier. 
- Click Create

Once it has completed, find the ACR in the resource group and note down the following information:

- Registry name, i.e. myAcrRegistry
- Login server, i.e. nyAcrRegistry.azurecr.io
- Click on Access Keys and copy one of the password fields. 

### Azure Kubernetes Service (AKS)
On the [AzurePortal](http://portal.azure.com), find the resource group you made. When you open it click Add
- Search for Kubernetes Service
- Click on the resulting <b>Kubernetes Service</b> in the list.
- Click create 
- It's fine to keep all defaults (but your cluster will be super tiny, but that's OK). 
- Just be sure that the service is being created in the resource group created earlier. 
- Click Review + Create

Once that has completed, note down the following information:

- Resource Group Name (which you probably should already have)
- Kubernetes Service Name

### Azure Data Science Virtual Machine (DSVM)
On the [AzurePortal](http://portal.azure.com), find the resource group you made. When you open it click Add
- Search for Data Science Virtual Machine
- Click on the resulting <b>Data Science Virtual Machine for Linux (Ubuntu)</b> in the list.
- Click create 
- It's fine to keep all defaults, but I find it much easier to use a username and password than setting up SSH keys. 
- Just be sure that the machine is being created in the resource group created earlier. 
- Click Review + Create

Once that has completed, note down the following information:

- Public IP Address
- Username supplied
- Password supplied. 

### Enable authentication between AKS and ACR
This is really important because AKS will not be able to pull our images from our ACR without it.

On the [AzurePortal](http://portal.azure.com), in the upper right hand corner, click on Cloud Shell. This will start a terminal in a few seconds.

After collecting your subscription id, go to the cloud shell prompt and type 
```
az account set -s [your subscripiton id]
```

Next, open the file and modify the top 4 variables with the resource group, ACR and AKS names you have collected from above. 

Copy the contents (except the comments) of the file and paste them into the cloud shell prompt. 

This should succeed without a problem, but if there is a problem do them one line at a time.

### X2GO Client
Now, this step is optional for you, but I typically have my main workstation Windows based, so I want a GUI interface to my Linux DSVM. 

To do this I use the X2GO Client. You can find instructions on how to do this [here](https://docs.microsoft.com/en-us/azure/machine-learning/data-science-virtual-machine/dsvm-ubuntu-intro#x2go).


# Lets get on with it already....

Yes, there is a bit of setup to get to this point, but that is the infrastructure we needed. So....the first thing you need to do is clone this repo to the Linux box you chose to use.

And...one more thing. To perform tasks against your AKS cluster, you will need to install <b>kubectl</b> from [this](https://kubernetes.io/docs/tasks/tools/install-kubectl/) on your Linux box....then you're done setting up infrastructure, I promise!

## Create the Docker container
In the source directory run the following commands:

```
sudo docker build -t myFlask:latest .
sudo docker run -d -p 5000:5000 myFlask
```

These steps build the container image (using Dockerfile and requirements.txt), then start it on the local machine. 

Open a browser and navigate to <i>localhost:5000</i> and you should see that the container is hit. 

Great, now kill the container

```
sudo docker ps
sudo docker kill [your container name]
```

## Log into the ACR
Next we need to log into the ACR we created earlier

```
sudo docker login -u [acrName] -p [acr password] [acrname].azurecr.io
```

## Tag and push your container to ACR
The next steps create a tag for your image and then push it to the ACR. Note that you are going to need to modify some content inside the deployimage.yaml file. Specifically, you will need to put in your acrName. 


```
sudo docker tag myFlask [acrname].azurecr.io/myFlask

sudo docker push [acrname].azurecr.io/myFlask
```

Great, at this point your container has been pushed to your ACR and we can finally get to moving it to the AKS cluster. 

## Set up the service on AKS
The next commands move your container from ACR to AKS as a deployment and then set up the service which will serve it up.

```
# Make SURE you have modified the deployimage.yaml with your ACR name
kubectl apply -f deployimage.yaml

# Now we need to create a service, your deployement name, if not changed from 
# the deployimage.yaml is my-deployment.
kubectl expose deploymnet/[deploymentName] --type=LoadBalancer --name=myFlask
```

This exposure is going to take some time.... but we can continue on....

## View the AKS dashboard

Run the command :
```
kubectl proxy
```

This starts a proxy on your machine to the cluster. While there are other ways to do this, it's MUCH easier to just open a browser and enter the following:

```
http://127.0.0.1:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/#!/node?namespace=default
```

<b>NOTE</b> If you still can't see the dashboard, you may need to issue the following command 

## That's it....
This should work for you, and I'll be working on it a bit to ensure it stays relevant, at least for a bit. 

Don't hesitate to reach out if you have questions. 