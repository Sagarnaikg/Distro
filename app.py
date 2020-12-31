from halo import Halo
import time
spinner = Halo(text='Loading', spinner='dots12')
spinner.start()

time.sleep(3)

spinner.stop()
