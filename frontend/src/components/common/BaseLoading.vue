<template>
  <div :class="loadingClasses">
    <div v-if="type === 'spinner'" class="base-loading-spinner">
      <div class="base-loading-spinner-dot" v-for="i in 3" :key="i" :style="dotStyle(i)"></div>
    </div>

    <div v-else-if="type === 'dots'" class="base-loading-dots">
      <div class="base-loading-dot" v-for="i in 3" :key="i" :style="dotAnimationStyle(i)"></div>
    </div>

    <div v-else class="base-loading-circle">
      <svg class="base-loading-circle-svg" viewBox="0 0 50 50">
        <circle class="base-loading-circle-background" cx="25" cy="25" r="20" fill="none" />
        <circle class="base-loading-circle-foreground" cx="25" cy="25" r="20" fill="none" />
      </svg>
    </div>

    <div v-if="text" class="base-loading-text">{{ text }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'spinner' | 'dots' | 'circle'
  text?: string
  size?: 'small' | 'medium' | 'large'
  color?: string
  fullscreen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'spinner',
  size: 'medium',
  color: '#FF6B35',
  fullscreen: false,
})

const loadingClasses = computed(() => {
  return [
    'base-loading',
    `base-loading--${props.size}`,
    {
      'base-loading--fullscreen': props.fullscreen,
    },
  ]
})

const dotStyle = (index: number) => {
  const rotation = (index - 1) * 120
  return {
    transform: `rotate(${rotation}deg)`,
  }
}

const dotAnimationStyle = (index: number) => {
  return {
    animationDelay: `${(index - 1) * 0.15}s`,
  }
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.base-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;

  &--fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.9);
    z-index: 9999;
  }

  &--small {
    .base-loading-spinner,
    .base-loading-dots,
    .base-loading-circle {
      width: 24px;
      height: 24px;
    }

    .base-loading-text {
      font-size: $font-size-sm;
    }
  }

  &--medium {
    .base-loading-spinner,
    .base-loading-dots,
    .base-loading-circle {
      width: 32px;
      height: 32px;
    }

    .base-loading-text {
      font-size: $font-size-md;
    }
  }

  &--large {
    .base-loading-spinner,
    .base-loading-dots,
    .base-loading-circle {
      width: 48px;
      height: 48px;
    }

    .base-loading-text {
      font-size: $font-size-lg;
    }
  }
}

.base-loading-spinner {
  position: relative;
  width: 32px;
  height: 32px;
}

.base-loading-spinner-dot {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;

  &::before {
    content: '';
    display: block;
    width: 20%;
    height: 20%;
    background-color: v-bind(color);
    border-radius: 50%;
    margin: 0 auto;
    animation: spinner-dot 1.2s infinite ease-in-out both;
  }
}

.base-loading-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.base-loading-dot {
  width: 8px;
  height: 8px;
  background-color: v-bind(color);
  border-radius: 50%;
  animation: dots-bounce 1.4s infinite ease-in-out both;
}

.base-loading-circle {
  width: 32px;
  height: 32px;
}

.base-loading-circle-svg {
  width: 100%;
  height: 100%;
  animation: circle-rotate 1.4s linear infinite;
}

.base-loading-circle-background {
  stroke: rgba(0, 0, 0, 0.1);
  stroke-width: 3;
}

.base-loading-circle-foreground {
  stroke: v-bind(color);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 90, 150;
  stroke-dashoffset: 0;
  animation: circle-dash 1.4s ease-in-out infinite;
}

.base-loading-text {
  color: $color-text-secondary;
  font-weight: 500;
  text-align: center;
}

@keyframes spinner-dot {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes dots-bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes circle-rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes circle-dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}
</style>