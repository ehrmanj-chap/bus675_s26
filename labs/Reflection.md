# Lab 2 Reflection

In this lab, both containers ran on your laptop. In production, the preprocessor would run in the warehouse datacenter and the inference API would run in Congo's main datacenter.

**How would the architecture and your `docker run` commands differ if these containers were actually running in separate datacenters?**

Consider:
- How would the preprocessor find the inference API?
- What about the shared volumes?
- What new challenges would arise?


## Your Reflection Below
# Reflection

Sorry, it's more paragraphs than you wanted. 

In this lab, both the preprocessor and inference API ran locally on the same laptop using Docker. In that setup, the two containers could communicate through a shared Docker network (`congo-net`) and the preprocessor could reach the inference API by container name (`http://congo-inference-container:8000`). This was more reliable than trying to use host-based routing from inside Docker given errors from my WSL Ubuntu environment. The preprocessor was configured to call `API_URL + "/predict"`, so on a shared Docker network the API URL could simply be the other container’s name and port. Meanwhile, both services used bind-mounted local folders so that the preprocessor could watch an `incoming/` directory and the API could write logs to a local `logs/` directory. This worked well because both containers were running on the same machine and could share the same local filesystem through mounted volumes.

If these containers were actually running in separate datacenters, the architecture would need to change significantly. First, the preprocessor would no longer be able to find the inference API through a Docker container name or a local network alias like `congo-inference-container`. Instead, it would need to call a real network address, such as a public or private DNS name like `https://inference.congo.internal` or a load balancer endpoint. In production, the inference API would likely sit behind a reverse proxy, API gateway, or load balancer, and the preprocessor would connect over HTTPS rather than plain HTTP. The API location would still be configured through an environment variable, but that variable would point to a real remote service rather than another container on the same Docker bridge network.

Second, the shared volumes would no longer work the same way. In the lab, both containers could rely on host-mounted folders such as `incoming/` and `logs/`, because they were both running on the same laptop. In separate datacenters, there would be no shared local filesystem between them. The warehouse-side preprocessor would likely read images from a warehouse file server, object storage bucket, or message queue rather than a host bind mount. Likewise, the inference API would not write logs to a folder on the preprocessor machine. Instead, logs would likely be written to centralized cloud storage, a logging platform, or a database. If the company still wanted to preserve processed images or metadata, that data would need to be uploaded to shared remote storage rather than moved into a local `/incoming/processed` directory that another service could also inspect.

The `docker run` commands would also differ. In the lab, the commands included bind mounts and a shared Docker network so the services could communicate locally. In production, the commands would probably not mount local host directories at all, since each container would run on its own server or orchestration platform. The preprocessor container would instead receive environment variables for a remote API URL, credentials, and perhaps the address of a shared storage service. The inference API container would expose its port to the datacenter network or sit behind a reverse proxy rather than relying on a laptop port mapping like `-p 8000:8000`. In practice, both services would likely be deployed with something more robust than raw `docker run`, such as Kubernetes, ECS, or another orchestration system.

Several new challenges would arise in the multi-datacenter version. Network latency would become important, since every image classification request would travel between datacenters rather than across a local Docker network. Reliability would also matter much more: the preprocessor would need retry logic, timeout handling, and perhaps a queue in case the inference API became temporarily unavailable. Security would become a major concern as well. The services would need authentication, encryption in transit, firewall rules, and tighter control over which systems were allowed to call the API. Monitoring and observability would also become more important, since debugging a failed request across datacenters is much harder than inspecting two local containers on one laptop.

Overall, the lab version used local Docker networking and shared bind mounts because both services lived on the same machine. The production version would replace those conveniences with real service discovery, remote storage, and secure cross-datacenter communication. In that sense, the `congo-net` solution I used during the lab is actually a simplified preview of the production idea: the preprocessor still needed a proper network-visible address for the inference API, rather than assuming that `localhost` or the host machine would always work.
