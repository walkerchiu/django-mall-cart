from setuptools import find_packages, setup

setup(
    name="django-mall-cart",
    version="1.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "Django>=4.2",
        "django-app-account>=1.0",
        "django-app-organization>=1.0",
        "django-mall-product>=1.0",
        "django-mall-shipment>=1.0",
    ],
    author="Walker Chiu",
    author_email="chenjen.chiou@gmail.com",
    description="",
    classifiers=[
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)
