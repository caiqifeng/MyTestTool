<template>
  <div :class="cardClasses" @click="handleClick">
    <div v-if="title || $slots.header" class="base-card-header">
      <slot name="header">
        <h3 v-if="title" class="base-card-title">{{ title }}</h3>
      </slot>
    </div>

    <div class="base-card-body">
      <slot />
    </div>

    <div v-if="$slots.footer" class="base-card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  shadow?: 'sm' | 'md' | 'lg' | 'xl' | 'none'
  bordered?: boolean
  clickable?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'sm',
  bordered: true,
  clickable: false,
  padding: 'md',
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardClasses = computed(() => {
  return [
    'base-card',
    `base-card--shadow-${props.shadow}`,
    `base-card--padding-${props.padding}`,
    {
      'base-card--bordered': props.bordered,
      'base-card--clickable': props.clickable,
    },
  ]
})

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.base-card {
  background: $color-white;
  border-radius: $border-radius-md;
  overflow: hidden;
  transition: all 0.2s ease;

  &--shadow-sm {
    box-shadow: $shadow-sm;
  }

  &--shadow-md {
    box-shadow: $shadow-md;
  }

  &--shadow-lg {
    box-shadow: $shadow-lg;
  }

  &--shadow-xl {
    box-shadow: $shadow-xl;
  }

  &--shadow-none {
    box-shadow: none;
  }

  &--bordered {
    border: 1px solid $color-border;
  }

  &--clickable {
    cursor: pointer;

    &:hover {
      box-shadow: $shadow-md;
      transform: translateY(-2px);
    }
  }

  &--padding-none {
    padding: 0;
  }

  &--padding-sm {
    padding: $spacing-sm;
  }

  &--padding-md {
    padding: $spacing-md;
  }

  &--padding-lg {
    padding: $spacing-lg;
  }
}

.base-card-header {
  padding: $spacing-md $spacing-md 0;
  margin-bottom: $spacing-sm;

  .base-card--padding-none & {
    padding: $spacing-md $spacing-md 0;
  }
}

.base-card-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $color-text-primary;
  margin: 0;
}

.base-card-body {
  .base-card--padding-none & {
    padding: 0;
  }

  .base-card--padding-sm & {
    padding: $spacing-sm;
  }

  .base-card--padding-md & {
    padding: $spacing-md;
  }

  .base-card--padding-lg & {
    padding: $spacing-lg;
  }
}

.base-card-footer {
  padding: 0 $spacing-md $spacing-md;
  margin-top: $spacing-sm;

  .base-card--padding-none & {
    padding: 0 $spacing-md $spacing-md;
  }
}
</style>