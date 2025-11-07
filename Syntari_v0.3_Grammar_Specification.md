# Syntari Programming Language Specification v0.3

## Core Philosophy
Syntari is an AI-augmented, type-safe, functional-first language designed for next-generation computation.
It merges deterministic logic, runtime flexibility, and direct AI integration for reasoning and optimization.

---

## 1. Lexical Structure

```
letter          = "A" … "Z" | "a" … "z" | "_" ;
digit           = "0" … "9" ;
alphanumeric    = letter | digit ;

identifier      = letter , { alphanumeric | "_" } ;
integer_literal = digit , { digit } ;
float_literal   = digit , { digit } , "." , { digit } ;
string_literal  = '"' , { character - '"' } , '"' ;
boolean_literal = "true" | "false" ;
```

Comments:
```
comment_single  = "//" , { any_char_except_newline } ;
comment_multi   = "/*" , { any_char } , "*/" ;
```

---

## 2. Program Structure

```
program         = { import_decl | type_decl | trait_decl | impl_decl | func_decl | statement } ;
import_decl     = "use" , identifier , { "." , identifier } ;
```

---

## 3. Declarations

### Types
```
type_decl       = "type" , identifier , "{" , { field_decl } , "}" ;
field_decl      = identifier , ":" , type_ref ;
```

### Traits
```
trait_decl      = "trait" , identifier , [ "<" , identifier , ">" ] , "{" ,
                    { func_signature } , "}" ;
func_signature  = "fn" , identifier , "(" , [ param_list ] , ")" ,
                    [ "->" , type_ref ] ;
```

### Implementations
```
impl_decl       = "impl" , identifier , [ "<" , identifier , ">" ] ,
                    "{" , { func_decl } , "}" ;
```

---

## 4. Functions

```
func_decl       = "fn" , identifier , "(" , [ param_list ] , ")" ,
                    [ "->" , type_ref ] , block ;
param_list      = param_decl , { "," , param_decl } ;
param_decl      = identifier , ":" , type_ref ;
```

---

## 5. Types and Generics

```
type_ref        = identifier , [ "<" , type_ref , { "," , type_ref } , ">" ] ;
```

---

## 6. Statements

```
statement       = var_decl
                | assign_stmt
                | if_stmt
                | while_stmt
                | return_stmt
                | expr_stmt
                | match_stmt
                ;
```

### Variable Declarations
```
var_decl        = ("let" | "const") , identifier , [ ":" , type_ref ] ,
                    "=" , expression ;
```

### Assignment
```
assign_stmt     = identifier , "=" , expression ;
```

### If Statement
```
if_stmt         = "if" , "(" , expression , ")" , block ,
                    [ "else" , block | "else" , if_stmt ] ;
```

### While Loop
```
while_stmt      = "while" , "(" , expression , ")" , block ;
```

### Return
```
return_stmt     = "return" , [ expression ] ;
```

### Expression Statement
```
expr_stmt       = expression ;
```

### Match Statement
```
match_stmt      = "match" , expression , "{" ,
                    { pattern_clause } , "}" ;
pattern_clause  = pattern , "->" , expression ;
pattern         = identifier | integer_literal | "_" ;
```

---

## 7. Blocks

```
block           = "{" , { statement } , "}" ;
```

---

## 8. Expressions

```
expression      = logical_or ;
logical_or      = logical_and , { "||" , logical_and } ;
logical_and     = equality , { "&&" , equality } ;
equality        = comparison , { ("==" | "!=") , comparison } ;
comparison      = term , { ("<" | "<=" | ">" | ">=") , term } ;
term            = factor , { ("+" | "-") , factor } ;
factor          = unary , { ("*" | "/" | "%") , unary } ;
unary           = [ "!" | "-" ] , primary ;
primary         = literal
                | identifier
                | call_expr
                | "(" , expression , ")"
                ;
call_expr       = identifier , "(" , [ arg_list ] , ")" ;
arg_list        = expression , { "," , expression } ;
```

---

## 9. Literals

```
literal         = integer_literal
                | float_literal
                | string_literal
                | boolean_literal
                ;
```

---

## 10. AI and System Intrinsics

```
ai_query        = "ai.query" , "(" , expression , ")" ;
ai_eval         = "ai.eval" , "(" , expression , ")" ;
ai_suggest      = "ai.suggest" , "(" , ")" ;
system_print    = "print" , "(" , expression , ")" ;
system_trace    = "trace" , "(" , ")" ;
```

---

## 11. Entry Point

```
entry_point     = "fn main()" , block ;
```

---

## 12. Notes

- Curly braces define scope; indentation is cosmetic.
- Functions, traits, and types are first-class.
- Generics resolved at compile time before bytecode emission.
- AI intrinsics sandboxed for secure deterministic use.

---

## Next Step

Next logical design phase: `.sbc` bytecode layout specification.
