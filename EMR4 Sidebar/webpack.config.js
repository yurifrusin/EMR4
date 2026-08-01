/* eslint-disable no-undef */

const path = require("path");
const devCerts = require("office-addin-dev-certs");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");

const urlDev = "https://localhost:3000/";
const urlProd = "__RAISA_PUBLIC_ORIGIN__/";

async function getHttpsOptions() {
  const httpsOptions = await devCerts.getHttpsServerOptions();
  return { ca: httpsOptions.ca, key: httpsOptions.key, cert: httpsOptions.cert };
}

module.exports = async (env, options) => {
  const dev = options.mode === "development";
  const config = {
    devtool: dev ? "source-map" : false,
    entry: {
      polyfill: ["core-js/stable", "regenerator-runtime/runtime"],
      taskpane: [
        "./src/taskpane/office-host-runtime.js",
        "./src/taskpane/clinician-one-document-context.js",
        "./src/taskpane/taskpane.js",
      ],
      commands: "./src/commands/commands.js",
    },
    output: {
      clean: true,
    },
    resolve: {
      extensions: [".html", ".js"],
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader",
          },
        },
        {
          test: /\.(png|jpg|jpeg|gif|ico)$/,
          type: "asset/resource",
          generator: {
            filename: "assets/[name][ext][query]",
          },
        },
      ],
    },
    plugins: [
      new HtmlWebpackPlugin({
        filename: "taskpane.html",
        template: "./src/taskpane/taskpane.html",
        chunks: ["polyfill", "taskpane"],
      }),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: "src/taskpane/assets/emr_cube1.png",
            to: "assets/emr_cube1.png",
          },
          {
            from: "assets/icon-32.png",
            to: "assets/icon-32.png",
          },
          {
            from: "assets/icon-80.png",
            to: "assets/[name][ext][query]",
          },
          {
            from: "manifest*.xml",
            to: "[name]" + "[ext]",
            transform(content) {
              if (dev) {
                return content;
              } else {
                return content.toString().replace(new RegExp(urlDev, "g"), urlProd);
              }
            },
          },
          {
            from: "src/taskpane/taskpane.css",
            to: "taskpane.css",
          },
          {
            from: "src/taskpane/hosting-policy.js",
            to: "hosting-policy.js",
          },
        ],
      }),
      new HtmlWebpackPlugin({
        filename: "commands.html",
        template: "./src/commands/commands.html",
        chunks: ["polyfill", "commands"],
      }),
    ],
    devServer: {
      static: [
        {
          directory: path.join(__dirname, "..", "docs", "diary"),
          publicPath: "/diary",
        },
        {
          directory: path.join(__dirname, "..", "docs", "images"),
          publicPath: "/images",
        },
      ],
      headers: {
        "Access-Control-Allow-Origin": "*",
      },
      server: {
        type: "https",
        options: env.WEBPACK_BUILD || options.https !== undefined ? options.https : await getHttpsOptions(),
      },
      host: "127.0.0.1",
      port: process.env.npm_package_config_dev_server_port || 3000,
    },
  };

  return config;
};
