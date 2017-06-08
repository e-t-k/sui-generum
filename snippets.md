Code and script snippets.


## Jupyter

### Notebook server with drive mounted

```
docker run --rm -it --name NAME-jupyter \
    -p 52820:8888 \
    -v `pwd`:/home/jovyan/work \
    -v /pod/MY/FILE/STORE:/data/FILESTORE:ro \
    -v /scratch/MYNAME:/scratch \
    jupyter/datascience-notebook start-notebook.sh \
    --NotebookApp.password='sha1:password:hash:goes:here’
```
Gives me a private notebook server, access to treehouse, my pwd, and scratch with a strong password 
 -  to generate password: http://jupyter-notebook.readthedocs.io/en/latest/public_server.html#preparing-a-hashed-password

