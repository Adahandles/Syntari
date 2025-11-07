# Syntari Programming Language

**Version:** 0.3  
**Owner:** DeuOS, LLC  
**License:** [Commercial License](Syntari_Commercial_License_DeuOS.md)

---

## Overview

**Syntari** is an AI-integrated, type-safe, functional-first programming language developed by **DeuOS, LLC**.  
It fuses deterministic computing, adaptive intelligence, and low-level performance into one unified ecosystem.

Syntari is designed to serve as the foundation for AI-driven systems, blockchain logic, and future autonomous computation environments.

---

## Key Features

- **AI-Native Language Core:** Built-in `core.ai` module allows reasoning, query, and adaptive optimization.  
- **Type Safety:** Static typing with inference through `core.type`.  
- **Functional Syntax:** Clean, expressive structure similar to Python and Haskell.  
- **JIT Compilation:** Executes `.sbc` bytecode through the Syntari virtual machine.  
- **Modular System:** Organized library structure for networking, AI, and system control.  
- **Secure by Design:** Sandbox execution and deterministic output for blockchain applications.

---

## Repository Structure

```
syntari/
├── README.md
├── Syntari_v0.3_Grammar_Specification.md
├── Syntari_Commercial_License_DeuOS.md
├── docs/
│   ├── LANGUAGE_SPEC.md
│   ├── BYTECODE_FORMAT.md
│   └── ROADMAP.md
├── src/
│   ├── interpreter/
│   ├── compiler/
│   ├── stdlib/
│   └── ai/
└── examples/
    ├── hello_world.syn
    └── ai_query_demo.syn
```

---

## Example

```syntari
use core.ai
use core.system

fn main() {
    print("Hello from Syntari.")
    let insight = ai.query("Summarize the purpose of this code.")
    print(insight)
}
```

Output:
```
Hello from Syntari.
This code prints a greeting and asks the AI to describe itself.
```

---

## Development Roadmap

| Version | Stage | Key Additions |
|----------|--------|----------------|
| 0.1 | Prototype | Base REPL, interpreter core |
| 0.2 | Stable | Arithmetic, logic, closures |
| 0.3 | Current | Type system, package manager, JIT compiler |
| 0.4 | Planned | Networking, web REPL, AI IDE |
| 0.5+ | Future | On-chain deterministic execution, neural plugin system |

---

## Legal Notice

Syntari is proprietary software owned by **DeuOS, LLC**.  
All rights reserved. Unauthorized redistribution, training, or open-source replication is strictly prohibited.

For commercial licensing, contact:  
**legal@deuos.io**

---

© 2025 DeuOS, LLC. All Rights Reserved.
