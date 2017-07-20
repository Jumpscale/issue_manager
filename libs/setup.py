import setuptools

setuptools.setup(name='issuemanagerlib',
                 version="1.0.0",
                 description='IssueManager library to be used by IssueManager portal application.',
                 long_description=open('README.md').read().strip(),
                 author='GreenItGlobe',
                 author_email='info@gig.tech',
                 url='https://github.com/Jumpscale/issue_manager',
                 packages=['issuemanagerlib'],
                 license='MIT License',
                 zip_safe=False,
                 keywords='issuemanager capnp jumpscale portal',
                 install_requires=[
                        'JumpScale9',
                 ],
                 classifiers=['Packages'])
