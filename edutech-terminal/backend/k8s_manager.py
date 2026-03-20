"""
Kubernetes Pod Manager - Production Implementation
For spawning and managing isolated terminal environments
"""

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
import asyncio
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class KubernetesPodManager:
    """Manage Kubernetes pods for terminal sessions"""
    
    def __init__(self, namespace: str = "edutech-terminal"):
        """Initialize Kubernetes client"""
        self.namespace = namespace
        
        # Load kubeconfig (in-cluster or local)
        try:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config")
        except config.ConfigException:
            config.load_kube_config()
            logger.info("Loaded local Kubernetes config")
        
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
    
    async def create_terminal_pod(
        self, 
        pod_name: str, 
        user_id: str,
        environment_type: str = "ubuntu"
    ) -> Dict:
        """
        Create isolated terminal pod for user
        
        Args:
            pod_name: Unique pod identifier
            user_id: User ID for labeling and tracking
            environment_type: Type of environment (ubuntu, docker, kubernetes)
        
        Returns:
            Pod metadata dictionary
        """
        
        # Select container image based on environment type
        images = {
            "ubuntu": "ubuntu:22.04",
            "docker": "docker:dind",
            "kubernetes": "edutech/kubernetes-lab:latest",
            "python": "python:3.11-slim",
            "node": "node:18-alpine"
        }
        
        image = images.get(environment_type, "ubuntu:22.04")
        
        # Define pod manifest
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": pod_name,
                "namespace": self.namespace,
                "labels": {
                    "app": "terminal",
                    "type": "user-session",
                    "user-id": user_id,
                    "environment": environment_type
                },
                "annotations": {
                    "created-by": "edutech-terminal-platform"
                }
            },
            "spec": {
                "containers": [{
                    "name": "terminal",
                    "image": image,
                    "command": ["/bin/bash"],
                    "args": ["-c", self._get_startup_script(environment_type)],
                    "stdin": True,
                    "stdinOnce": False,
                    "tty": True,
                    "resources": {
                        "requests": {
                            "memory": "512Mi",
                            "cpu": "250m"
                        },
                        "limits": {
                            "memory": "2Gi",
                            "cpu": "1000m",
                            "ephemeral-storage": "10Gi"
                        }
                    },
                    "securityContext": {
                        "runAsNonRoot": True,
                        "runAsUser": 1000,
                        "allowPrivilegeEscalation": False,
                        "capabilities": {
                            "drop": ["ALL"]
                        },
                        "readOnlyRootFilesystem": False
                    },
                    "volumeMounts": [{
                        "name": "user-workspace",
                        "mountPath": "/home/learner"
                    }]
                }],
                "volumes": [{
                    "name": "user-workspace",
                    "emptyDir": {
                        "sizeLimit": "10Gi"
                    }
                }],
                "restartPolicy": "Never",
                "terminationGracePeriodSeconds": 30,
                "automountServiceAccountToken": False
            }
        }
        
        try:
            # Create pod
            pod = self.v1.create_namespaced_pod(
                namespace=self.namespace,
                body=pod_manifest
            )
            
            logger.info(f"Created pod {pod_name} for user {user_id}")
            
            # Wait for pod to be running
            await self._wait_for_pod_ready(pod_name)
            
            return {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "ip": pod.status.pod_ip
            }
            
        except ApiException as e:
            logger.error(f"Failed to create pod {pod_name}: {e}")
            raise
    
    def _get_startup_script(self, environment_type: str) -> str:
        """Get startup script based on environment type"""
        
        scripts = {
            "ubuntu": """
                apt-get update -qq && \
                apt-get install -y -qq vim git curl wget python3 python3-pip nodejs npm && \
                useradd -m -s /bin/bash learner && \
                echo 'learner ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
                su - learner -c '/bin/bash'
            """,
            "docker": """
                apk add --no-cache bash vim git curl wget python3 py3-pip nodejs npm && \
                adduser -D -s /bin/bash learner && \
                su - learner -c '/bin/bash'
            """,
            "kubernetes": """
                apt-get update -qq && \
                apt-get install -y -qq vim git curl wget kubectl helm && \
                useradd -m -s /bin/bash learner && \
                su - learner -c '/bin/bash'
            """,
            "python": """
                pip install --no-cache-dir ipython jupyter && \
                useradd -m -s /bin/bash learner && \
                su - learner