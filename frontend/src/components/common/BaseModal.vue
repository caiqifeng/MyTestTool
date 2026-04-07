<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="visible" class="base-modal-overlay" @click.self="handleOverlayClick">
        <div :class="modalClasses" :style="{ maxWidth: width }">
          <div v-if="showHeader" class="base-modal-header">
            <h3 v-if="title" class="base-modal-title">{{ title }}</h3>
            <button v-if="showClose" class="base-modal-close" @click="handleClose">
              ×
            </button>
          </div>

          <div class="base-modal-body">
            <slot />
          </div>

          <div v-if="$slots.footer" class="base-modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useSlots } from 'vue'

interface Props {
  visible: boolean
  title?: string
  width?: string
  showHeader?: boolean
  showClose?: boolean
  closeOnOverlayClick?: boolean
  closeOnEsc?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  width: '500px',
  showHeader: true,
  showClose: true,
  closeOnOverlayClick: true,
  closeOnEsc: true,
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  close: []
}>()

const modalClasses = computed(() => {
  return [
    'base-modal',
    {
      'base-modal--has-header': props.showHeader,
      'base-modal--has-footer': !!useSlots().footer,
    },
  ]
})

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleOverlayClick = () => {
  if (props.closeOnOverlayClick) {
    handleClose()
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (props.closeOnEsc && event.key === 'Escape' && props.visible) {
    handleClose()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';

.base-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: $spacing-md;
}

.base-modal {
  background: $color-white;
  border-radius: $border-radius-lg;
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: $shadow-xl;
}

.base-modal-header {
  padding: $spacing-lg $spacing-lg $spacing-md;
  border-bottom: 1px solid $color-border;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.base-modal-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: $color-text-primary;
  margin: 0;
}

.base-modal-close {
  background: none;
  border: none;
  font-size: $font-size-xxl;
  color: $color-text-tertiary;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: color 0.2s ease;

  &:hover {
    color: $color-text-primary;
  }
}

.base-modal-body {
  padding: $spacing-lg;
  overflow-y: auto;
  flex: 1;
}

.base-modal-footer {
  padding: $spacing-md $spacing-lg $spacing-lg;
  border-top: 1px solid $color-border;
  display: flex;
  justify-content: flex-end;
  gap: $spacing-sm;
  flex-shrink: 0;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .base-modal,
.modal-fade-leave-active .base-modal {
  transition: transform 0.3s ease;
}

.modal-fade-enter-from .base-modal,
.modal-fade-leave-to .base-modal {
  transform: scale(0.9);
}
</style>