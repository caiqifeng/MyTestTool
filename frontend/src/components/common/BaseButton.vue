<template>
  <button
    :class="buttonClasses"
    :type="htmlType"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="button-loading">
      <span class="button-loading-spinner"></span>
      <span v-if="loadingText" class="button-loading-text">{{ loadingText }}</span>
    </span>

    <span v-else class="button-content">
      <span v-if="$slots.icon" class="button-icon">
        <slot name="icon" />
      </span>
      <span class="button-text">
        <slot />
      </span>
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  block?: boolean
  round?: boolean
  htmlType?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  disabled: false,
  loading: false,
  loadingText: '',
  block: false,
  round: false,
  htmlType: 'button',
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  return [
    'base-button',
    `base-button--${props.type}`,
    `base-button--${props.size}`,
    {
      'base-button--disabled': props.disabled,
      'base-button--loading': props.loading,
      'base-button--block': props.block,
      'base-button--round': props.round,
    },
  ]
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: $border-radius-md;
  font-family: $font-family;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
  user-select: none;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &--primary {
    background-color: $color-primary;
    color: $color-white;

    &:hover:not(:disabled) {
      background-color: $color-primary-light;
    }

    &:active:not(:disabled) {
      background-color: $color-primary-dark;
    }
  }

  &--secondary {
    background-color: $color-secondary;
    color: $color-white;

    &:hover:not(:disabled) {
      background-color: $color-secondary-light;
    }

    &:active:not(:disabled) {
      background-color: $color-secondary-dark;
    }
  }

  &--ghost {
    background-color: transparent;
    color: $color-primary;
    border: 1px solid $color-primary;

    &:hover:not(:disabled) {
      background-color: rgba($color-primary, 0.1);
    }
  }

  &--danger {
    background-color: $color-error;
    color: $color-white;

    &:hover:not(:disabled) {
      background-color: lighten($color-error, 10%);
    }
  }

  &--small {
    padding: $spacing-xs $spacing-sm;
    font-size: $font-size-sm;
    height: 32px;
  }

  &--medium {
    padding: $spacing-sm $spacing-md;
    font-size: $font-size-md;
    height: 40px;
  }

  &--large {
    padding: $spacing-md $spacing-lg;
    font-size: $font-size-lg;
    height: 48px;
  }

  &--block {
    width: 100%;
  }

  &--round {
    border-radius: $border-radius-round;
  }

  &--loading {
    cursor: wait;
  }
}

.button-content {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
}

.button-icon {
  display: flex;
  align-items: center;
}

.button-loading {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
}

.button-loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: $color-white;
  border-radius: 50%;
  animation: button-spin 0.8s linear infinite;
}

@keyframes button-spin {
  to {
    transform: rotate(360deg);
  }
}

.button-loading-text {
  font-size: $font-size-sm;
}
</style>