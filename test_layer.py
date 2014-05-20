import logging
logging.basicConfig()
import dag_on as dag

@dag.func
def times2():
    return gvar.get() * 2

gvar = dag.var(20)

if __name__ == "__main__":
    #dag.set_log_level(logging.DEBUG)
    print times2()

    with dag.layer('test') as l:
        gvar.set(30)
        print times2()

    with l:
        gvar.set(40)
        print times2()
        
    with l:
        print times2()
        
    print times2()
    
    with dag.temp_layer():
        gvar.set(100)
        print times2()
        
    print times2()
    
    if dag.dag:
        print dag.dag.get_layers()
    
    