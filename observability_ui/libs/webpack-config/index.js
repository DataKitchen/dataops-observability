const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');
const mf = require('@angular-architects/module-federation/webpack');
const path = require('path');
const { libs } = require("./libs");
const { mappedPaths } = require("./mapped-paths");


module.exports.CreateConfig = function(moduleFedarationConfig, mappings, extraAliases) {
  const workspaceRootPath = process.env.NX_WORKSPACE_ROOT ?? path.join(__dirname, '../../');
  const tsConfigPath = process.env.NX_TSCONFIG_PATH ?? path.join(workspaceRootPath, 'tsconfig.base.json');

  const sharedMappings = new mf.SharedMappings();
  sharedMappings.register(tsConfigPath, mappings ?? mappedPaths, workspaceRootPath);

  const sharedLibraries = mf.share({
    ...libs,
    ...sharedMappings.getDescriptors(),
  }, workspaceRootPath);

  const config = {
    library: {
      type: 'module',
    },
    shared: sharedLibraries,
    filename: 'remoteEntry.js',
    ...moduleFedarationConfig,
  };

  return {
    module: {
      rules: [
        {
          test: /\.tpl/,
          type: 'asset/source',
        }
      ],
    },
    output: {
      uniqueName: config.name,
      publicPath: 'auto',
    },
    optimization: {
      runtimeChunk: false,
    },
    experiments: {
      outputModule: true,
    },
    resolve: {
      alias: {
        ...sharedMappings.getAliases(),
        ...(extraAliases ?? {}),
      },
    },
    plugins: [
      new ModuleFederationPlugin({ ...config }),
      sharedMappings.getPlugin(),
    ],
  };
}
