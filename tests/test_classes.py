"""
Tests for OOP/Classes in Syntari v0.4
"""

import pytest
from src.interpreter.lexer import Lexer
from src.interpreter.parser import Parser
from src.interpreter.interpreter import Interpreter, ClassInstance


def parse_and_run(code: str) -> Interpreter:
    """Helper to parse and run code"""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    return interpreter


class TestClassBasics:
    """Test basic class functionality"""

    def test_class_declaration(self):
        """Test declaring a class"""
        code = """
        class MyClass {
            x = 10;
        }
        """
        interp = parse_and_run(code)
        # Class should be defined in environment
        assert "MyClass" in interp.environment.variables

    def test_create_instance(self):
        """Test creating class instance with new"""
        code = """
        class MyClass {
            x = 10;
        }
        let obj = new MyClass();
        """
        interp = parse_and_run(code)
        obj = interp.environment.get("obj")
        assert isinstance(obj, ClassInstance)

    def test_access_property(self):
        """Test accessing object property"""
        code = """
        class MyClass {
            value = 42;
        }
        let obj = new MyClass();
        let result = obj.value;
        """
        interp = parse_and_run(code)
        result = interp.environment.get("result")
        assert result == 42  # Properties are initialized with their default values


class TestConstructor:
    """Test constructor functionality"""

    def test_constructor_sets_properties(self):
        """Test that constructor can set properties"""
        code = """
        class Person {
            name = "";
            age = 0;
            
            fn constructor(n, a) {
                this.name = n;
                this.age = a;
            }
        }
        let p = new Person("Alice", 30);
        """
        interp = parse_and_run(code)
        p = interp.environment.get("p")
        assert p.properties["name"] == "Alice"
        assert p.properties["age"] == 30

    def test_constructor_with_no_params(self):
        """Test constructor with no parameters"""
        code = """
        class Counter {
            count = 0;
            
            fn constructor() {
                this.count = 0;
            }
        }
        let c = new Counter();
        """
        interp = parse_and_run(code)
        c = interp.environment.get("c")
        assert c.properties["count"] == 0


class TestMethods:
    """Test class methods"""

    def test_simple_method(self):
        """Test calling a simple method"""
        code = """
        class Greeter {
            message = "";
            
            fn constructor(msg) {
                this.message = msg;
            }
            
            fn greet() {
                print(this.message);
            }
        }
        let g = new Greeter("Hello");
        g.greet();
        """
        # Should not raise
        parse_and_run(code)

    def test_method_with_parameters(self):
        """Test method with parameters"""
        code = """
        class Calculator {
            fn add(a, b) -> int {
                return a + b;
            }
        }
        let calc = new Calculator();
        let result = calc.add(5, 3);
        """
        interp = parse_and_run(code)
        result = interp.environment.get("result")
        assert result == 8

    def test_method_accessing_properties(self):
        """Test method accessing object properties"""
        code = """
        class Counter {
            count = 0;
            
            fn increment() {
                this.count = this.count + 1;
            }
            
            fn get_count() -> int {
                return this.count;
            }
        }
        let c = new Counter();
        c.increment();
        c.increment();
        let result = c.get_count();
        """
        interp = parse_and_run(code)
        result = interp.environment.get("result")
        assert result == 2


class TestPropertyAccess:
    """Test property access and assignment"""

    def test_get_property(self):
        """Test getting property value"""
        code = """
        class Box {
            value = 0;
            
            fn constructor(v) {
                this.value = v;
            }
        }
        let b = new Box(42);
        let x = b.value;
        """
        interp = parse_and_run(code)
        x = interp.environment.get("x")
        assert x == 42

    def test_set_property(self):
        """Test setting property value"""
        code = """
        class Box {
            value = 0;
        }
        let b = new Box();
        b.value = 100;
        """
        interp = parse_and_run(code)
        b = interp.environment.get("b")
        assert b.properties["value"] == 100

    def test_modify_property(self):
        """Test modifying property"""
        code = """
        class Counter {
            count = 0;
            
            fn constructor() {
                this.count = 0;
            }
        }
        let c = new Counter();
        c.count = c.count + 10;
        """
        interp = parse_and_run(code)
        c = interp.environment.get("c")
        assert c.properties["count"] == 10


class TestComplexClasses:
    """Test complex class scenarios"""

    def test_multiple_instances(self):
        """Test creating multiple instances"""
        code = """
        class Point {
            x = 0;
            y = 0;
            
            fn constructor(x_val, y_val) {
                this.x = x_val;
                this.y = y_val;
            }
        }
        let p1 = new Point(10, 20);
        let p2 = new Point(30, 40);
        """
        interp = parse_and_run(code)
        p1 = interp.environment.get("p1")
        p2 = interp.environment.get("p2")
        assert p1.properties["x"] == 10
        assert p1.properties["y"] == 20
        assert p2.properties["x"] == 30
        assert p2.properties["y"] == 40

    def test_method_chain(self):
        """Test chaining method calls"""
        code = """
        class StringBuilder {
            text = "";
            
            fn constructor() {
                this.text = "";
            }
            
            fn append(s) {
                this.text = this.text + s;
            }
            
            fn get_text() {
                return this.text;
            }
        }
        let sb = new StringBuilder();
        sb.append("Hello");
        sb.append(" ");
        sb.append("World");
        let result = sb.get_text();
        """
        interp = parse_and_run(code)
        result = interp.environment.get("result")
        assert result == "Hello World"

    def test_this_in_nested_call(self):
        """Test this reference in nested method calls"""
        code = """
        class Calculator {
            value = 0;
            
            fn set(v) {
                this.value = v;
            }
            
            fn double() {
                this.set(this.value * 2);
            }
        }
        let calc = new Calculator();
        calc.set(5);
        calc.double();
        let result = calc.value;
        """
        interp = parse_and_run(code)
        result = interp.environment.get("result")
        assert result == 10
