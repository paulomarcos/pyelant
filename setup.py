from distutils.core import setup

with open('README.md') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
  name = 'pyelant',
  packages = ['pyelant'],
  version = '0.1',
  license = 'MIT',
  description = 'Python tool for easily performing translations and storing it on the clipboard.',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  author = 'Paulo Marcos',
  author_email = 'paulomarcos@me.com',
  url = 'https://github.com/paulomarcos/pyelant/',
  download_url = 'https://github.com/paulomarcos/pyelant/archive/v_01.tar.gz',
  keywords = ['translation', 'clipboard', 'easy'],
  install_requires = requirements
)