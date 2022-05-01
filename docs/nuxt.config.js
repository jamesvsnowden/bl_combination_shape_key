import theme from '@nuxt/content-theme-docs'

export default theme({
  server: {
    port: 4010
  },
  docs: {
    primaryColor: '#00CD81'
  },
  i18n: {
    locales: () => [{
      code: 'en',
      iso: 'en-US',
      file: 'en-US.js',
      name: 'English'
    }],
    defaultLocale: 'en'
  },
  buildModules: [
    
  ]
})
