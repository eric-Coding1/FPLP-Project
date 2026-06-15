"""FPLP Language → C++ Transpiler"""

import os, sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fplp.lexer import Lexer
from fplp.parser import Parser
from fplp.ast_nodes import *
from fplp.builtins import BUILTINS


def transpile(source):
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    return CppGen().generate(program)


CPP_RUNTIME = r'''// FPLP Runtime
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <variant>
#include <functional>
#include <cmath>
#include <memory>
#include <sstream>
#include <algorithm>
#include <random>
#include <chrono>
#include <cstdint>
using namespace std;

struct Value;
using ValueList = vector<Value>;
using ValueMap = map<string, Value>;
using FnType = function<Value(const vector<Value>&)>;

struct Value {
    variant<monostate,bool,int64_t,double,string,ValueList,ValueMap,FnType> data;
    Value():data(monostate{}){}
    Value(nullptr_t):data(monostate{}){}
    Value(bool v):data(v){}
    Value(int v):data(int64_t(v)){}
    Value(int64_t v):data(v){}
    Value(double v):data(v){}
    Value(const char*v):data(string(v)){}
    Value(const string&v):data(v){}
    Value(ValueList v):data(move(v)){}
    Value(ValueMap v):data(move(v)){}
    Value(FnType f):data(move(f)){}

    bool is_nil()const{return holds_alternative<monostate>(data);}
    bool is_int()const{return holds_alternative<int64_t>(data);}
    bool is_float()const{return holds_alternative<double>(data);}
    bool is_string()const{return holds_alternative<string>(data);}
    bool is_bool()const{return holds_alternative<bool>(data);}
    bool is_array()const{return holds_alternative<ValueList>(data);}
    bool is_map()const{return holds_alternative<ValueMap>(data);}
    bool is_fn()const{return holds_alternative<FnType>(data);}

    bool truthy()const{
        if(is_nil())return false;
        if(is_bool())return get<bool>(data);
        if(is_int())return get<int64_t>(data)!=0;
        if(is_float())return get<double>(data)!=0.0;
        if(is_string())return !get<string>(data).empty();
        if(is_array())return !get<ValueList>(data).empty();
        if(is_map())return !get<ValueMap>(data).empty();
        return true;
    }

    string str()const{
        if(is_nil())return"nil";
        if(is_bool())return get<bool>(data)?"true":"false";
        if(is_int())return to_string(get<int64_t>(data));
        if(is_float()){
            ostringstream ss;ss<<get<double>(data);
            string s=ss.str();
            auto p=s.find_last_not_of('0');
            if(p!=string::npos){s=s.substr(0,p+1);if(s.back()=='.')s.pop_back();}
            return s;
        }
        if(is_string())return get<string>(data);
        if(is_array()){
            string r="[";for(size_t i=0;i<get<ValueList>(data).size();i++){if(i)r+=", ";r+=get<ValueList>(data)[i].str();}return r+"]";
        }
        if(is_map()){
            string r="{";bool f=true;
            for(auto&[k,v]:get<ValueMap>(data)){if(!f)r+=", ";r+=k+": "+v.str();f=false;}return r+"}";
        }
        return"<fn>";
    }

    Value operator+(const Value&r)const{
        if(is_string()||r.is_string())return str()+r.str();
        if(is_int()&&r.is_int())return get<int64_t>(data)+get<int64_t>(r.data);
        return (is_int()?(double)get<int64_t>(data):get<double>(data)) + (r.is_int()?(double)get<int64_t>(r.data):get<double>(r.data));
    }
    Value operator-(const Value&r)const{
        if(is_int()&&r.is_int())return get<int64_t>(data)-get<int64_t>(r.data);
        return (is_int()?(double)get<int64_t>(data):get<double>(data)) - (r.is_int()?(double)get<int64_t>(r.data):get<double>(r.data));
    }
    Value operator*(const Value&r)const{
        if(is_int()&&r.is_int())return get<int64_t>(data)*get<int64_t>(r.data);
        return (is_int()?(double)get<int64_t>(data):get<double>(data)) * (r.is_int()?(double)get<int64_t>(r.data):get<double>(r.data));
    }
    Value operator/(const Value&r)const{
        if(is_int()&&r.is_int()){
            int64_t b=get<int64_t>(r.data);if(b==0)throw runtime_error("div by zero");
            int64_t a=get<int64_t>(data);if(a%b==0)return a/b;
            return (double)a/(double)b;
        }
        return (is_int()?(double)get<int64_t>(data):get<double>(data))/(r.is_int()?(double)get<int64_t>(r.data):get<double>(r.data));
    }
    Value operator%(const Value&r)const{return get<int64_t>(data)%get<int64_t>(r.data);}
    Value operator-()const{if(is_int())return -get<int64_t>(data);return -get<double>(data);}
    bool operator==(const Value&r)const{return data==r.data;}
    bool operator<(const Value&r)const{
        if(is_int()&&r.is_int())return get<int64_t>(data)<get<int64_t>(r.data);
        return (is_int()?(double)get<int64_t>(data):get<double>(data))<(r.is_int()?(double)get<int64_t>(r.data):get<double>(r.data));
    }
};

struct Env{
    map<string,Value> store;
    shared_ptr<Env> outer;
    Env():outer(nullptr){}
    Env(shared_ptr<Env> o):outer(o){}
    Value*find(const string&n){
        auto i=store.find(n);if(i!=store.end())return&i->second;
        if(outer)return outer->find(n);return nullptr;
    }
    void set(const string&n,const Value&v){store[n]=v;}
};

Value _print(const vector<Value>&a){
    for(size_t i=0;i<a.size();i++){if(i)cout<<" ";cout<<a[i].str();}cout<<endl;return nullptr;
}
Value _len(const vector<Value>&a){
    auto&v=a[0];if(v.is_string())return(int64_t)v.str().size();
    if(v.is_array())return(int64_t)get<ValueList>(v.data).size();
    if(v.is_map())return(int64_t)get<ValueMap>(v.data).size();return nullptr;
}
Value _sqrt(const vector<Value>&a){return sqrt(a[0].is_int()?(double)a[0].str().size()?0:0:0);}
// NOTE: _sqrt needs proper impl - use this instead
Value _sqrt2(const vector<Value>&a){
    double d=a[0].is_int()?(double)get<int64_t>(a[0].data):get<double>(a[0].data);
    return sqrt(d);
}
Value _push(const vector<Value>&a){auto&arr=const_cast<Value&>(a[0]);get<ValueList>(arr.data).push_back(a[1]);return arr;}
Value _pop(const vector<Value>&a){auto&arr=const_cast<Value&>(a[0]);if(get<ValueList>(arr.data).empty())return nullptr;Value v=get<ValueList>(arr.data).back();get<ValueList>(arr.data).pop_back();return v;}
Value _int(const vector<Value>&a){auto&v=a[0];if(v.is_int())return v;if(v.is_float())return(int64_t)get<double>(v.data);if(v.is_string())return(int64_t)stoll(get<string>(v.data));return nullptr;}
Value _float(const vector<Value>&a){auto&v=a[0];if(v.is_float())return v;if(v.is_int())return(double)get<int64_t>(v.data);if(v.is_string())return stod(get<string>(v.data));return nullptr;}
Value _str(const vector<Value>&a){return a[0].str();}
Value _abs(const vector<Value>&a){auto&v=a[0];if(v.is_int())return abs(get<int64_t>(v.data));return abs(get<double>(v.data));}
'''


class CppGen:
    def __init__(self):
        self._output = []
        self._indent = 0
        self._builtin_names = set(BUILTINS.keys())
        self._user_fns = {}

    def emit(self, line=""):
        if line:
            self._output.append("    " * self._indent + line)
        else:
            self._output.append("")

    def generate(self, program):
        self._output = []
        self.emit(CPP_RUNTIME)
        self.emit()

        # Collect user fns
        for stmt in program.statements:
            if isinstance(stmt, LetStatement) and isinstance(stmt.value, FnLiteral):
                self._user_fns[stmt.name.value] = (stmt.value.parameters, stmt.value.body)

        self.emit("int main() {")
        self._indent = 1
        self.emit('map<string,FnType> B = {')
        self._indent = 2
        for name in ['print','len','sqrt','abs','push','pop','int','float','str']:
            # Use generic dispatch names
            pass
        # Simpler: just call by function pointer
        self._indent = 1
        self.emit("};")
        self.emit("auto env = make_shared<Env>();")
        self.emit()

        # Emit user functions
        for name, (params, body) in self._user_fns.items():
            self._emit_fn(name, params, body)

        # Emit main body
        for stmt in program.statements:
            self._emit_stmt(stmt)

        self.emit("return 0;")
        self._indent = 0
        self.emit("}")
        return '\n'.join(self._output)

    def _emit_fn(self, name, params, body):
        self.emit(f'env->set("{name}", FnType([env](const vector<Value>& a)->Value{{')
        self._indent = 2
        for i, p in enumerate(params):
            self.emit(f'auto _{p.value} = a[{i}];')
        for s in body.statements:
            if isinstance(s, ExpressionStatement) and isinstance(s.expression, InfixExpression) \
                    and s.expression.operator == '+' and isinstance(s.expression.left, Identifier) \
                    and isinstance(s.expression.right, Identifier):
                # Arrow function auto-return: fn(x,y)=>x+y becomes { return x + y; }
                # But the block wraps it as ExpressionStatement
                pass
            self._emit_stmt(s)
        self.emit("return Value(nullptr);")
        self._indent = 1
        self.emit("}));")
        self.emit()

    def _emit_stmt(self, node):
        t = type(node)
        if t is ExpressionStatement:
            code = self._expr(node.expression)
            self.emit(code + ";")
        elif t is LetStatement:
            if isinstance(node.value, FnLiteral):
                return  # already handled
            code = self._expr(node.value)
            self.emit(f'env->set("{node.name.value}", {code});')
        elif t is AssignStatement:
            code = self._expr(node.value)
            self.emit(f'*env->find("{node.name}") = {code};')
        elif t is ReturnStatement:
            if node.value:
                code = self._expr(node.value)
                self.emit(f"return {code};")
            else:
                self.emit("return Value(nullptr);")
        elif t is BlockStatement:
            for s in node.statements:
                self._emit_stmt(s)
        elif t is IfExpression:
            cond = self._expr(node.condition)
            self.emit(f"if(({cond}).truthy()){{")
            self._indent += 1
            self._emit_stmt(node.consequence)
            self._indent -= 1
            self.emit("}")
            if node.alternative:
                self.emit("else{")
                self._indent += 1
                self._emit_stmt(node.alternative)
                self._indent -= 1
                self.emit("}")
        elif t is LoopExpression:
            if node.is_while:
                cond = self._expr(node.iterable)
                self.emit(f"while(({cond}).truthy()){{")
                self._indent += 1
                self._emit_stmt(node.body)
                self._indent -= 1
                self.emit("}")
            else:
                # for x in iterable { body }
                code = self._expr(node.iterable)
                self.emit(f"{{auto _it={code};int64_t _i=0,_n=(int64_t)_it.val().size();")
                # Need to get the right ValueList access. For arrays from literals.
                self.emit(f'while(_i<_n){{env->set("{node.identifier}",_it.val()[_i]);')
                self._indent += 1
                self._emit_stmt(node.body)
                self._indent -= 1
                self.emit("_i++;}}}")

    def _expr(self, node):
        """Return C++ expression string for a node."""
        t = type(node)
        if t is Identifier:
            name = node.value
            if name in self._builtin_names:
                return f'_builtin_{name}'
            return f'*env->find("{name}")'
        elif t is NumberLiteral:
            v = node.value
            if isinstance(v, int):
                return f'Value((int64_t){v})'
            return f'Value({v})'
        elif t is StringLiteral:
            s = node.value.replace('\\', '\\\\').replace('"', '\\"')
            return f'Value("{s}")'
        elif t is BooleanLiteral:
            return f'Value({str(node.value).lower()})'
        elif t is NilLiteral:
            return "Value(nullptr)"
        elif t is ArrayLiteral:
            els = ", ".join(self._expr(e) for e in node.elements)
            return f'Value(ValueList{{{els}}})'
        elif t is MapLiteral:
            pairs = []
            for k, v in node.pairs.items():
                kcode = self._expr(k)
                vcode = self._expr(v)
                pairs.append(f'{{{kcode}.str(),{vcode}}}')
            return f'Value(ValueMap{{{",".join(pairs)}}})'
        elif t is PrefixExpression:
            r = self._expr(node.right)
            if node.operator == '-':
                return f'-({r})'
            elif node.operator in ('not', '!'):
                return f'!bool(({r}).truthy())'
            return r
        elif t is InfixExpression:
            op = node.operator
            l = self._expr(node.left)
            r = self._expr(node.right)
            if op == 'and':
                return f'Value(bool(({l}).truthy()&&({r}).truthy()))'
            elif op == 'or':
                return f'Value(bool(({l}).truthy()||({r}).truthy()))'
            elif op == '=':
                if isinstance(node.left, Identifier):
                    return f'(*env->find("{node.left.value}")={r})'
                return f'({l}={r})'
            elif op == '==':
                return f'Value(({l})==({r}))'
            elif op == '!=':
                return f'Value(!(({l})==({r})))'
            elif op == '<':
                return f'Value(({l})<({r}))'
            elif op == '>':
                return f'({l})>({r})'  # No Value() wrapping - needs fix
            else:
                return f'({l}){op}({r})'
        elif t is CallExpression:
            fn = self._expr(node.function)
            args = ", ".join(self._expr(a) for a in node.arguments)
            return f'{fn}({{{args}}})'
        elif t is IndexExpression:
            obj = self._expr(node.left)
            idx = self._expr(node.index)
            return f'({obj})[{idx}]'
        elif t is FnLiteral:
            params_code = ", ".join(f'Value _{p.value}' for p in node.parameters)
            return f'FnType([env](const vector<Value>& a)->Value{{return Value(nullptr);}})'
        return "Value(nullptr)"
