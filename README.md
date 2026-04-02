# MOdular Testbed for Researching Attacks (MOTRA) - setups

<p align="center">
  <img src=assets/motra.jpeg?raw=true" alt="motra logo" width="350"/>
</p>

MOTRA is a flexible framework for creating testbeds tailored to the user's needs.

Its main features are its modularity and extensibility through packaging testbed components as containerized applications. Docker is the containerization solution of choice. This repository contains ready-to-use Docker compose simulation setups. There is a [companion](https://github.com/Laboratory-for-Safe-and-Secure-Systems/motra-images) repository available which contains images referenced in the compose files.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project was created so collect sources for testbed components. We needed quickly adaptable and configurable testbeds to perform specific penetration tests against different components and implementations. As we realized, there are few open-source projects available to draw from, so we decided to make ours available to the public and use the community to extend it to any domain they see fit.

The core project currently contains two demos for testing different device configurations. The full demo configurations are found in `simple-water-treatment-plant/...` and can all be run using `docker compose`. The dmz demo uses additional devices to forward data using a DMZ service between an IT and an OT domain. Demo files and forward services, as well as an additional dashboard, are hosted in the *-demo folders and can be customized. 
  

## Getting Started

### Prerequisites

The project only requires a working Docker engine. We try to use the latest version for testing our images, but it can work with older versions. Currently, we use:

```bash
docker >= 28.0
```

### Usage

After cloning the repository, you can inspect and modify the compose files. The repository is organized as follows:

```bash
/setup-name
  README - contains explanation of setup
  compose.yaml
  # config files or any other sources needed
```

## Contributing

If you want to contribute setups yourself, feel free to open pull requests. Please add a README that briefly explains what the setup does and how it can be used. You can reach out to us by opening an issue.

## License

GPLv3 License – see LICENSE for details.
