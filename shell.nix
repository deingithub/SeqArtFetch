{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python3.withPackages(
      ps: with ps; [ black pylint lxml cssselect aiohttp setuptools ]
    )) 
  ];

  # For VSCode, easily-accessible symlinks to the nix-shell's linter/formatter
  shellHook = ''
  rm ./nix-shell-black 2> /dev/null
  rm ./nix-shell-pylint 2> /dev/null
  ln -s `which black` ./nix-shell-black 2> /dev/null
  ln -s `which pylint` ./nix-shell-pylint 2> /dev/null
  '';
}
