package com.jdb.trading.config

import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.http.client.SimpleClientHttpRequestFactory
import org.springframework.web.client.RestTemplate

/**
 * Configuration for RestTemplate used for external API calls
 */
@Configuration
class RestTemplateConfig {

    @Bean
    fun restTemplate(): RestTemplate {
        val factory = SimpleClientHttpRequestFactory().apply {
            setConnectTimeout(5000)  // 5 seconds connection timeout
            setReadTimeout(10000)     // 10 seconds read timeout
        }

        return RestTemplate(factory)
    }
}
