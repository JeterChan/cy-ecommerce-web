import { createI18n } from 'vue-i18n'
import zhTW from './locales/zh-TW.json'

export const i18n = createI18n({
  legacy: false,
  locale: 'zh-TW',
  fallbackLocale: 'zh-TW',
  messages: {
    'zh-TW': zhTW
  }
})

