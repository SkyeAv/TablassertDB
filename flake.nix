{
  description = "tbdb";
  inputs = {
    systems.url = "github:nix-systems/x86_64-linux";
    nixpkgs.url = "github:nixos/nixpkgs/25.05";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };
  outputs = inputs @ {self, systems, nixpkgs, flake-parts, ...}:
  flake-parts.lib.mkFlake {inherit inputs;} {
    systems = import inputs.systems;
    imports = [
      ./nix/app.nix
    ];
  };
}