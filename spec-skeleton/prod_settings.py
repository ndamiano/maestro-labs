"""Point the local control plane at RunPod: prod's queue block, pennyroyal llm block, the funnel
URL as cp_url, one pod per queue so spend stays bounded. Usage: prod_settings.py <cp_url>"""
import json, sys
p = "/home/nick/Documents/ai-agent-test/src/config/settings.json"
s = json.load(open(p))
cp_url = sys.argv[1].rstrip("/")
s["llm"] = {"model": "pennyroyal", "max_tokens": 50000, "reasoning": "medium",
            "n_ctx": 131072, "slots": 2, "sglang_args": ""}
s["workqueue"]["job_timeout_seconds"] = 2400
s["workqueue"]["lease_seconds"] = max(int(s["workqueue"].get("lease_seconds", 60)), 120)
q = {
 "llm": {"template_id": "mcss4tfwhs", "gpu_type_ids": ["NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA RTX PRO 6000 Blackwell Server Edition"], "max_workers": 1, "cooldown_seconds": 300, "idle_exit_seconds": 90, "boot_deadline_seconds": 300, "allowed_cuda_versions": ["13.0"], "network_volume_ids": ["juqk1aq0ew", "szjxc7ha34"], "boot_seconds": 240, "min_jobs_per_pod": 6},
 "image": {"template_id": "mv8x54x4y4", "gpu_type_ids": ["NVIDIA GeForce RTX 5090", "NVIDIA RTX PRO 4500 Blackwell"], "max_workers": 1, "cooldown_seconds": 90, "idle_exit_seconds": 30, "boot_deadline_seconds": 300, "allowed_cuda_versions": ["13.0"], "boot_seconds": 90, "min_jobs_per_pod": 6},
 "mesh": {"template_id": "57gdpfynya", "gpu_type_ids": ["NVIDIA GeForce RTX 5090", "NVIDIA RTX PRO 4500 Blackwell"], "max_workers": 1, "cooldown_seconds": 90, "idle_exit_seconds": 120, "boot_deadline_seconds": 300, "boot_seconds": 150, "min_jobs_per_pod": 6},
}
s["runpod"] = {**s["runpod"], "enabled": True, "cp_url": cp_url, "network_volume_id": "6jqgopakyi", "tick_seconds": 2, "queues": q}
json.dump(s, open(p, "w"), indent=2); open(p, "a").write("\n")
print("settings written for", cp_url)
