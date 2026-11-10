function readPackage(pkg) {
  if (pkg.dependencies && pkg.dependencies['minimatch']) {
    pkg.dependencies['minimatch'] = '^11.0.0';
  }
  if (pkg.devDependencies && pkg.devDependencies['minimatch']) {
    pkg.devDependencies['minimatch'] = '^11.0.0';
  }
  if (pkg.peerDependencies && pkg.peerDependencies['minimatch']) {
    pkg.peerDependencies['minimatch'] = '^11.0.0';
  }
  return pkg;
}

module.exports = {
  hooks: {
    readPackage,
  },
};
