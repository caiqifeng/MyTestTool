import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from './BaseButton.vue'

describe('BaseButton', () => {
  it('renders with default props', () => {
    const wrapper = mount(BaseButton, {
      slots: {
        default: 'Click me',
      },
    })

    expect(wrapper.text()).toContain('Click me')
    expect(wrapper.classes()).toContain('base-button--primary')
    expect(wrapper.classes()).toContain('base-button--medium')
  })

  it('renders with different type', () => {
    const wrapper = mount(BaseButton, {
      props: {
        type: 'secondary',
      },
      slots: {
        default: 'Secondary',
      },
    })

    expect(wrapper.classes()).toContain('base-button--secondary')
  })

  it('renders with different size', () => {
    const wrapper = mount(BaseButton, {
      props: {
        size: 'large',
      },
      slots: {
        default: 'Large',
      },
    })

    expect(wrapper.classes()).toContain('base-button--large')
  })

  it('renders disabled state', () => {
    const wrapper = mount(BaseButton, {
      props: {
        disabled: true,
      },
      slots: {
        default: 'Disabled',
      },
    })

    expect(wrapper.classes()).toContain('base-button--disabled')
    expect(wrapper.find('button').element.disabled).toBe(true)
  })

  it('renders loading state', () => {
    const wrapper = mount(BaseButton, {
      props: {
        loading: true,
      },
      slots: {
        default: 'Loading',
      },
    })

    expect(wrapper.classes()).toContain('base-button--loading')
    expect(wrapper.find('.button-loading-spinner').exists()).toBe(true)
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(BaseButton, {
      slots: {
        default: 'Click me',
      },
    })

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('click')
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(BaseButton, {
      props: {
        disabled: true,
      },
      slots: {
        default: 'Disabled',
      },
    })

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted()).not.toHaveProperty('click')
  })

  it('does not emit click when loading', async () => {
    const wrapper = mount(BaseButton, {
      props: {
        loading: true,
      },
      slots: {
        default: 'Loading',
      },
    })

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted()).not.toHaveProperty('click')
  })
})