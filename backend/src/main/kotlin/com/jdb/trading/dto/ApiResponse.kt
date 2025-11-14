package com.jdb.trading.dto

import java.time.Instant

/**
 * Generic API response wrapper matching frontend ApiResponse<T> interface
 */
data class ApiResponse<T>(
    val success: Boolean,
    val data: T,
    val message: String? = null,
    val timestamp: String = Instant.now().toString()
) {
    companion object {
        fun <T> success(data: T, message: String? = null) =
            ApiResponse(success = true, data = data, message = message)

        fun <T> error(data: T, message: String) =
            ApiResponse(success = false, data = data, message = message)
    }
}
