{inputs, ...}:
{
  perSystem = {system, config, ...}:
    let
      pkgs = import inputs.nixpkgs {inherit system;};
      lib = pkgs.lib;
      pg = pkgs.postgresql_16;
      pgloader = pkgs.pgloader;
      pgPort = ''''${TBDB_PORT:-5432}'';
      pgUser = ''''${TBDB_USER:-multiomics}'';
      pgName = ''''${TBDB_NAME:-TBDB}'';
      py = pkgs.python313Packages;
    in
    {
      devShells.default = pkgs.mkShell {
        packages = with config.packages; [
          tbdb-init
          tbdb-build
          tbdb-stop
        ];
      };
      packages = {
        tbdb-init = pkgs.writeShellApplication {
          name = "tbdb-init";
          runtimeInputs = [
            pkgs.coreutils
            pg
          ];
          text = ''
            set -euo pipefail

            DATADIR="''${1:-.pgdata}"
            RUNDIR="''${2:-.pg_run}"
            
            mkdir -p "$RUNDIR"
            if [ -f "$DATADIR/PG_VERSION" ]; then
              echo "FLAKE-CODE:1 | Already Intitialized... $DATADIR"
              exit 0
            fi

            initdb -D "$DATADIR" -U "${pgUser}" -A trust --encoding=UTF8 --locale=C

            {
              echo "unix_socket_directories = '$(pwd)/$RUNDIR'"
              echo "port = ${pgUser}"
            } >> "$DATADIR/postgresql.conf"

            pg_ctl -D "$DATADIR" -l "$DATADIR/postgres.log" -o "-k $(pwd)/$RUNDIR -p ${pgPort}" start

            INITSQL="CREATE DATABASE \"${pgName}\" OWNER \"${pgUser}\""
            psql -h "$(pwd)/$RUNDIR" -p "${pgUser}" -U "${pgUser}" -d postgres -c "$INITSQL"

            echo "FLAKE-CODE:2 | Sucessfully Intilialized $DATADIR..."
            echo "psql -h $(pwd)/$RUNDIR -p ${pgPort} -U ${pgUser} ${pgName}"
          '';
        };
        tbdb-build = py.buildPythonApplication {
          pname = "tbdb";
          version = "0.1.0";
          src = ../.;
          pyproject = true;
          build-system = with py; [
            setuptools
          ];
          propagatedBuildInputs = with py; [
            ruamel-yaml
            pydantic
            typer
          ];
          postInstall = ''
            mkdir -p $out/share/sql
            cp -r src/tbdb/sql/* $out/share/sql/
          '';
          nativeBuildInputs = [
            pkgs.makeWrapper
            pgloader
          ];
          makeWrapperArgs = [
            "--set TBDB_PORT ${pgPort}"
            "--set TBDB_USER ${pgUser}"
            "--set TBDB_NAME ${pgName}"
            "--set TBDB_SQL_PATH $out/share/sql"
          ];
        };
        tbdb-stop = pkgs.writeShellApplication {
          name = "tbdb-stop";
          runtimeInputs = [
            pg
          ];
          text = ''
            set -euo pipefail

            DATADIR="''${1:-.pgdata}"

            if [ -f "$DATADIR/PG_VERSION" ]; then
              pg_ctl -D "$DATADIR" stop -m fast
              echo "FLAKE-CODE:3 | Stopped $DATADIR"
            else
              echo "FLAKE-CODE:4 | No Postgres Found... $DATADIR"
            fi
          '';
        };
      };
    };
}
