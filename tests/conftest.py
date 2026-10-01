# test_hierarchical_isolation.py pytest testi degil, calistirilabilir bir demo.
# Icindeki `from brian2 import *` Brian2'nin `test` fonksiyonunu da ice aktariyor;
# pytest bunu test sanip Brian2'nin kendi test paketinin tamamini calistiriyordu.
collect_ignore = ["test_hierarchical_isolation.py"]
