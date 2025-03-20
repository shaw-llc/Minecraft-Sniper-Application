module.exports = {
  packagerConfig: {
    asar: true,
    icon: './assets/icon',
    extraResource: [
      './src/python'
    ],
    appBundleId: 'com.openmc.usernameSniper',
    appCategoryType: 'public.app-category.utilities',
    osxSign: {
      identity: null
    }
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        name: 'openmc_username_sniper',
        setupIcon: './assets/icon.ico',
        iconUrl: 'https://raw.githubusercontent.com/shaw-llc/Minecraft-Sniper-Application/master/assets/icon.ico',
        loadingGif: './assets/installer.gif'
      }
    },
    {
      name: '@electron-forge/maker-zip',
      platforms: [
        'darwin'
      ]
    },
    {
      name: '@electron-forge/maker-dmg',
      config: {
        format: 'ULFO',
        icon: './assets/icon.icns',
        background: './assets/dmg-background.png',
        window: {
          width: 540,
          height: 380
        }
      }
    },
    {
      name: '@electron-forge/maker-deb',
      config: {
        options: {
          icon: './assets/icon.png',
          categories: [
            'Utility'
          ]
        }
      }
    },
    {
      name: '@electron-forge/maker-rpm',
      config: {
        options: {
          icon: './assets/icon.png'
        }
      }
    }
  ],
  publishers: [
    {
      name: '@electron-forge/publisher-github',
      config: {
        repository: {
          owner: 'shaw-llc',
          name: 'Minecraft-Sniper-Application'
        },
        prerelease: false,
        draft: true
      }
    }
  ]
}; 