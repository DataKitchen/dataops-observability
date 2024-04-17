const { CreateConfig } = require('../../libs/webpack-config');
const moduleFedarationConfig = require('./module-federation.config');

module.exports = CreateConfig(moduleFedarationConfig);
