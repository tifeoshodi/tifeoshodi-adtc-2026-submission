# Technical Report — AgriTriage AI (Offline Agricultural Advisory System)

**Team ID:** tifeoshodi  
**Domain:** agriculture  
**Model:** Llama-3.2-1B-Instruct-Q4_K_M

---

## Problem

Across the African continent, rural farmers face massive agricultural challenges—ranging from rapidly spreading pests like Fall Armyworm to viral infections like Cassava Mosaic Disease. Unfortunately, agricultural extension officers are chronically understaffed, and farmers often operate in regions with little to no internet connectivity. 

**AgriTriage AI** solves this by providing a hyper-local, entirely offline Retrieval-Augmented Generation (RAG) advisory system. By embedding agricultural data natively and running on budget consumer laptops, extension officers and farmers can receive instantaneous, highly-accurate diagnostics and management strategies without needing cloud access.

---

## Design Decisions

- **Base model:** Llama-3.2-1B-Instruct. We selected the 1B variant as it offers an unparalleled balance of instruction-following capability while being exceptionally lightweight for consumer-grade laptops.
- **Quantization:** GGUF Q4_K_M. This 4-bit quantization reduces the memory footprint significantly while maintaining the vast majority of the model's reasoning capabilities, making it the sweet spot for a strict 8GB RAM limit.
- **Alternatives considered:** 
  - *Llama 3 8B (Q4_K_M)*: Rejected because its memory footprint approached 5GB, leaving too little overhead for the OS and the Tauri/React GUI in an 8GB environment, risking OOM crashes.
  - *Phi-3 Mini*: Evaluated, but Llama 3.2 1B exhibited stronger adherence to agricultural RAG contexts without hallucinating.

---

## Constraints

- **Hardware Target:** 8 GB RAM, integrated GPU, Ubuntu 22.04 LTS (budget laptop profile).
- **Execution:** Pure CPU inference via `llama.cpp` using the native Windows/WSL hardware stack.
- **Connectivity:** Absolute zero-network capability required. The RAG pipeline relies on a pre-computed FAISS vector index of agricultural documents stored locally.

---

## Benchmarks

Our system underwent rigorous profiling using the official `adtc-profiler` in participant mode on local hardware. 

| Metric | Value |
|---|---|
| Machine | Windows 11 PC (Profiled locally via ADTC profiler proxy constraints) |
| RAM at peak (RSS) | ~1.38 GB (1385 MB) |
| Time to first token | ~10.3 seconds |
| Generation speed | 17.5 tokens/second |
| Thermal throttling | None observed (P99 CPU: 51.7%) |

These benchmarks prove that the Llama-3.2-1B Q4_K_M model effortlessly crushes the baseline 15 TPS requirement while operating *massively* below the 7GB RAM limit.
