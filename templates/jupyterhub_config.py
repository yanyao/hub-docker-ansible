c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.JupyterHub.hub_ip='{{hub_hostname}}'
notebook_dir =  '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container

#volume_prefix='hub-teaching'
volume_prefix='{{volume_prefix}}'
volume_from_vg='{{vgname}}'
c.DockerSpawner.prefix=volume_prefix
c.DockerSpawner.volumes = { volume_prefix+'-{username}' : notebook_dir }
#c.DockerSpawner.image = 'openjupyter/base-notebook-ppc64le:1.1.0'
#openjupyter/jupyter-base-cpu-ppc64le:v6.0.0
c.DockerSpawner.image = '{{base_image}}'
c.DockerSpawner.use_internal_ip=True
c.DockerSpawner.network_name='{{hub_network}}'
c.DockerSpawner.remove=True
admin_users=[{% for item in admin_users %} "{{item}}", {% endfor %}]
#gpu_users=["yanyao","g1","g2","g3"]
#gpu_user_dict={'0':None,'1':None,'2':None,'3':None}
c.Authenticator.admin_users = admin_users

{% if auth_class == 'native' %}
c.JupyterHub.authenticator_class = 'nativeauthenticator.NativeAuthenticator'
{% elif auth_class == 'ldap' %}
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address='ldap'
c.LDAPAuthenticator.lookup_dn = False
c.LDAPAuthenticator.bind_dn_template = [ {% for item in ldap.bind_dn_template %} "{{item}}", {% endfor %} ]
c.LDAPAuthenticator.escape_userdn = False
{% else %}

c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
{% endif %}

import docker
def create_vol_hook(spawner):
    username = spawner.user.name
    client =  docker.DockerClient(base_url='unix://var/run/docker.sock')
    client.volumes.create(name=volume_prefix+'-'+username,driver='lvm',driver_opts={'size':'{{volume_size}}','vg':volume_from_vg})
c.Spawner.pre_spawn_hook = create_vol_hook


{%if cpu_period and cpu_quota %}
c.DockerSpawner.extra_host_config=dict(cpu_period={{cpu_period|int}},cpu_quota={{cpu_quota|int}})
{% endif %}

{% if mem_limit %}
c.Spawner.mem_limt="{{mem_limit}}"
{% endif %}

{% if cull_enable %}
import sys
c.JupyterHub.services = [
    {
        'name': 'cull-idle',
        'admin': True,
        'command': [sys.executable, 'cull_idle_servers.py', '--timeout={{cull_timeout|int}}'],
    }
]
{%endif %}

{% if hub_extra_config %}
{{ hub_extra_config }}
{% endif %}


