# Syntari Programming Language

**Version:** 0.3  
**Owner:** DeuOS, LLC  
**License:** [Commercial License](Syntari_Commercial_License_DeuOS.md)

---

## 🚀 Quick Start

```bash
# Run a Syntari program
python3 main.py hello_world.syn

# Start interactive REPL
python3 main.py --repl

# Try examples
python3 main.py examples/functions.syn
```

📖 **[Read Getting Started Guide](GETTING_STARTED.md)** - Learn the most logical order to understand and use Syntari

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

## 🚀 Development Planning & Next Steps

**New to the project?** Start here:

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - 🎯 **START HERE** - Most logical order for learning, using, and extending Syntari
- **[DEVELOPMENT_SUMMARY.md](DEVELOPMENT_SUMMARY.md)** - 📋 Executive summary and project overview
- **[ROADMAP_VISUAL.md](ROADMAP_VISUAL.md)** - 🗺️ Visual roadmap with timelines and dependencies
- **[ACTION_ITEMS.md](ACTION_ITEMS.md)** - ✅ Prioritized 2-week task breakdown
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - 🔧 Code examples and implementation tutorials
- **[NEXT_STEPS.md](NEXT_STEPS.md)** - 📚 Comprehensive strategic planning for v0.4+

**Current Status:** 🎉 **v0.3 Complete!** Full interpreter pipeline functional with 189 passing tests. CLI, REPL, and examples ready. See [GETTING_STARTED.md](GETTING_STARTED.md) for usage.

---

## Legal Notice

Syntari is proprietary software owned by **DeuOS, LLC**.  
All rights reserved. Unauthorized redistribution, training, or open-source replication is strictly prohibited.

For commercial licensing, contact:  
**legal@deuos.io**

---

© 2025 DeuOS, LLC. All Rights Reserved.
