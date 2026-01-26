# Syntari Programming Language

**Version:** 0.4 (in development)  
**Owner:** DeuOS, LLC  
**License:** [Commercial License](Syntari_Commercial_License_DeuOS.md)

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Adahandles/Syntari.git
cd Syntari

# Run setup script
./setup.sh

# Or manually install
pip install -e .
```

### Usage

```bash
# Run a Syntari program
python3 main.py hello_world.syn

# Start interactive REPL
python3 main.py --repl

# Profile performance
python3 main.py --profile examples/functions.syn

# Run benchmarks
make benchmark

# Try examples
python3 main.py examples/functions.syn

# Run tests
make test
```

📖 **[Read Getting Started Guide](GETTING_STARTED.md)** - Learn the most logical order to understand and use Syntari

👨‍💻 **[Read Contributing Guide](CONTRIBUTING.md)** - Set up your development environment

🔒 **[Read Security Guide](SECURITY_GUIDE.md)** - Security best practices and tools

⚡ **[Read Performance Guide](PERFORMANCE_PROFILING.md)** - Profiling and benchmarking tools

---

## 🔒 Security

Syntari takes security seriously. Our repository includes:

- ✅ Automated security scanning (Bandit, Safety, pip-audit)
- ✅ Pre-commit hooks for secret detection
- ✅ Weekly security audits via GitHub Actions
- ✅ SSRF protection in networking module
- ✅ Comprehensive security documentation

**Quick Security Check:**
```bash
make security          # Run security checks
./cleanup.sh          # Clean repository
pre-commit install    # Set up hooks
```

See [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for details.

---

## ⚡ Performance

Syntari includes comprehensive performance profiling and benchmarking:

- **Performance Profiler** - Track execution metrics, hot paths, function timing
- **Benchmark Suite** - 5 benchmarks covering different workloads
- **Comparative Analysis** - Track improvements across versions
- **Multiple Formats** - Text, JSON, and HTML reports

**Quick Performance Check:**
```bash
make benchmark                    # Run all benchmarks
make profile FILE=script.syn      # Profile a script
make profile-html FILE=script.syn # Generate HTML report
```

**v0.3 Baseline (Interpreter):** ~290K-510K instructions/second  
**v0.4 Target (Bytecode VM):** 1.5-5M instructions/second (5-10x faster)

See [PERFORMANCE_PROFILING.md](PERFORMANCE_PROFILING.md) for details.

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
| 0.3 | ✅ Complete | Type system, full interpreter (296 tests) |
| 0.4 | 🚧 In Progress | Enhanced bytecode compiler, VM v2, performance profiler |
| 0.5 | Planned | Package manager, web REPL, AI IDE |
| 0.6+ | Future | On-chain execution, neural plugin system |

**Current Focus:** Performance optimization, bytecode compilation, profiling tools

---

## 🚀 Development Planning & Next Steps

**New to the project?** Start here:

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - 🎯 **START HERE** - Most logical order for learning, using, and extending Syntari
- **[DEVELOPMENT_SUMMARY.md](DEVELOPMENT_SUMMARY.md)** - 📋 Executive summary and project overview
- **[V04_DEVELOPMENT_PLAN.md](V04_DEVELOPMENT_PLAN.md)** - 📈 v0.4 development plan (8.5 weeks)
- **[ROADMAP_VISUAL.md](ROADMAP_VISUAL.md)** - 🗺️ Visual roadmap with timelines and dependencies
- **[ACTION_ITEMS.md](ACTION_ITEMS.md)** - ✅ Prioritized 2-week task breakdown
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - 🔧 Code examples and implementation tutorials
- **[NEXT_STEPS.md](NEXT_STEPS.md)** - 📚 Comprehensive strategic planning for v0.4+
- **[PERFORMANCE_PROFILING.md](PERFORMANCE_PROFILING.md)** - ⚡ Performance profiling and benchmarking

**Current Status:** 🚀 **v0.4 Development Phase 1 Complete!**
- ✅ Enhanced bytecode compiler v2 (900+ lines)
- ✅ Enhanced VM runtime v2 (700+ lines)
- ✅ Optimization framework (constant folding, dead code elimination)
- ✅ Performance profiler with HTML reports
- ✅ Benchmark suite (5 benchmarks)
- ✅ 296 tests passing
- 🚧 Next: Package manager foundation

---

## Legal Notice

Syntari is proprietary software owned by **DeuOS, LLC**.  
All rights reserved. Unauthorized redistribution, training, or open-source replication is strictly prohibited.

For commercial licensing, contact:  
**legal@deuos.io**

---

© 2025 DeuOS, LLC. All Rights Reserved.
