try:
    import rif.compiler as C
    C.Compiler(plugin='megadrive').build('examples/megadrive')
    print('OK')
except Exception as e:
    import traceback
    traceback.print_exc()
