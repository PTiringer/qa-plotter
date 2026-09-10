# Install and deploy

## Python installation

The package declares Python `>=3.10` and `nomad-lab>=1.4.3`. The parent
`nomad-distro-dev` workspace uses Python 3.12. Use Python 3.12 for this project's
setup and an environment compatible with the installed NOMAD version.

For a standalone checkout:

```sh
git clone https://github.com/PTiringer/qa-plotter.git
cd qa-plotter
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install .
qa-plotter-scrape --help
```

Installing the package registers its NOMAD entry points and the scraper command.
Merely copying the source directory onto a server does not register the plugin.
For editable development, see [Contributing](contribute_to_this_plugin.md).

## Install in the distribution workspace

From the parent `nomad-distro-dev` repository:

```sh
git submodule update --init --recursive
```

The repository must contain the `packages/qa-plotter` Git submodule registration,
a committed submodule revision, and the `qa-plotter` workspace dependency in
`pyproject.toml`. The submodule URL is
`https://github.com/PTiringer/qa-plotter.git`.

The project's deployment script builds the NOMAD image and installs the local
plugins, including `qa-plotter`. Its plugin layer uses `--no-deps`: dependencies
must already be present in the base image. The current scraper requires
`requests`; the plugin also declares NOMAD and FastAPI dependencies. When adding
new dependencies, update the image build as well as the Python package metadata.

## Deploy a plugin update

1. Commit and push the changes inside the `qa-plotter` repository.
2. In `nomad-distro-dev`, commit and push the updated `packages/qa-plotter`
   submodule revision to the deployment branch.
3. From the sibling `test_deployment` directory, run:

   ```sh
   ./deploy.sh update
   ```

The script defaults to branch `stable` and checkout `/opt/nomad-oasis`.
`update` fetches repository and submodule changes. `start` does not fetch them.
Enable image building (`BUILD_NOMAD_IMAGE=true`) to include changed plugin code.
Use the full image build when deploying GUI changes, such as the overview's plot
ordering. That GUI code belongs to `nomad-FAIR`, whose updated submodule revision
must also be committed in the parent repository.

After deployment, reprocess existing QA entries to regenerate their data and
figures. Updating the image does not rewrite existing archives by itself.

## Verify the installation

The scraper's `--help` output verifies the console command registration without
contacting MANATI. Processing the [tutorial's archive](../tutorial/tutorial.md)
verifies the schema, normalizer, and figure generation together.

For automatic scraping, network access must work from the processing worker,
not just from your laptop or the NOMAD web application. Configure the source as
described in [Usage](use_this_plugin.md).

If Docker reports that `packages/qa-plotter` is missing during `COPY`, check the
deployment checkout's `.gitmodules` and submodule revision. A local, uncommitted
registration cannot be fetched by the deployment script.
