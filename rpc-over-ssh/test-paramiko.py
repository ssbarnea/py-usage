import os
import paramiko
import inspect
import colorama

colorama.init()

f = inspect.getfile( inspect.currentframe())
s = inspect.stack()
cwd = os.path.dirname(os.path.abspath(f))


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())

privatekeyfile  = os.path.expanduser('~/.ssh/id_rsa')
pkey = paramiko.RSAKey.from_private_key_file(privatekeyfile, password='kato589')

#pkey = paramiko.RSAKey.from_private_key("sAPpmLh6GvASX80qu3GnnAK2mFzVvRbiMuZIeyqJZaMRe7F6LSIHbAjuY7cvje9bXYftfCe7hlmQGt5ZzEd1AsyqdDOm3dCIxyw15riLAlyzH3afu5+8qrNltV4LZg1/qpf4MTSBk1Pm+BhKy98FUBlfjXj2OibKqmLzvB/WaH+T0tRTKEyQDFDpUt6l53rAyxBzRpJtiYUTTlJTs/Jcec3GfkvvtRBs2M2H76xSmbrJ1I6y4af4NdVtWlKZ0z769qbZYeeCCH/PXRdYv7jvNYPmUKDtmqeseyOhpLgUfSkMAML/E4caK2MlNCN6xd5fAJUoC1+TENvrnxJ4HNlN+3T3S8NiysDC6nwYghX+mcYk0AmAHORXS/FlXAo/u/IK6Hk/N2HbyCH5Czte2KSQa9fkApPeptnB3tC0WFJKzvBTtVbxMkkng+YR4B+QW/2baVjtPIMsJErKuKazzFItu9pGctLBgMn7SAaZQanw/CIk7ol6tRnCdDudLv8yn0XddbX2Qkg/h/OaTuPjcLItFx4fKGyffpMNJk/jX+Umax5fnxMTMfZ391aY8P/JQUBPWg9w4/EBiOIkdiXiPPj7izhJaUC0u134s2cCPyWmarr91e3jMrNE1e0eVBQgCEn91AXTE8MuuDvU3UFoqrxWoBIGsWmBY1FLhHynm+i9yDeSLJKeS6zZgtSfWjpRShUtPwJbiQTvf5UvFF2Olt3rF6oFIW3M2Uyou9vBtN7S7+f9600yP/KITmyWyMyAFpWt69+1R1VLXmFpphI9vuuRoHX2B9U0fuPKNr1nRqlVqFg=rsolkYs=")
ssh.connect('127.0.0.1', username='user', pkey=pkey)

(r_stdin, r_stdout, r_stderr) = ssh.exec_command("dir")
lines = r_stdout.readlines()
print lines