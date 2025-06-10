<template>
  <div class="sankey-container" ref="sankeyContainer">
    <svg ref="sankeyEl"></svg>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import { sankey, sankeyLinkHorizontal } from 'd3-sankey'
import { useTheme } from 'vuetify'

export default {
  name: 'D3SankeyChart',
  props: {
    data: {
      type: Object,
      required: true
    },
    width: {
      type: Number,
      default: 800
    },
    height: {
      type: Number,
      default: 500
    }
  },
  setup(props) {
    const sankeyEl = ref(null)
    const sankeyContainer = ref(null)
    const theme = useTheme()

    const formatCurrency = (value) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value)
    }

    const createSankey = () => {
      if (!sankeyEl.value || !props.data?.datasets?.[0]?.data?.length) return

      // Clear previous chart
      d3.select(sankeyEl.value).selectAll('*').remove()


      // Get container dimensions
      const containerWidth = sankeyContainer.value?.clientWidth || props.width
      const containerHeight = props.height

      // Set up margins
      const margin = { top: 40, right: 120, bottom: 40, left: 120 }
      const width = containerWidth - margin.left - margin.right
      const height = containerHeight - margin.top - margin.bottom

      // Set up SVG
      const svg = d3.select(sankeyEl.value)
        .attr('width', containerWidth)
        .attr('height', containerHeight)

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      // Process data from chartjs format to d3-sankey format
      const sankeyData = props.data.datasets[0].data
      const nodesSet = new Set()
      const links = []

      // First pass: collect all unique node names
      sankeyData.forEach(d => {
        nodesSet.add(d.from)
        nodesSet.add(d.to)
      })

      // Create nodes array with proper structure
      const nodes = Array.from(nodesSet).map(name => ({
        name: name,
        id: name
      }))

      // Create links with proper node references
      sankeyData.forEach(d => {
        links.push({
          source: d.from,
          target: d.to,
          value: d.flow
        })
      })

      // Set up sankey generator with proper nodeId function
      const sankeyGenerator = sankey()
        .nodeId(d => d.name)
        .nodeWidth(20)
        .nodePadding(30)
        .extent([[0, 0], [width, height]])

      // Generate sankey layout
      const sankeyGraph = {
        nodes: nodes.map(d => ({ ...d })),
        links: links.map(d => ({ ...d }))
      }

      const { nodes: sankeyNodes, links: sankeyLinks } = sankeyGenerator(sankeyGraph)

      // Theme colors
      const isDark = theme.global.current.value.dark
      const textColor = isDark ? '#FFFFFF' : '#000000'
      const nodeColor = isDark ? '#64B5F6' : '#1976D2'

      // Create a color mapping based on target category names (excluding "Total Expenses")
      const categoryNodes = sankeyNodes.filter(d => d.name !== 'Total Expenses')
      const colorScale = d3.scaleOrdinal()
        .domain(categoryNodes.map(d => d.name))
        .range(d3.schemeCategory10)

      // Create links
      const link = g.append('g')
        .selectAll('.link')
        .data(sankeyLinks)
        .enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', sankeyLinkHorizontal())
        .attr('stroke', d => colorScale(d.target.name))
        .attr('stroke-width', d => Math.max(1, d.width))
        .attr('fill', 'none')
        .attr('opacity', 0.6)
        .on('mouseover', function(event, d) {
          d3.select(this).attr('opacity', 0.8)
          
          // Show tooltip
          const tooltip = d3.select('body').append('div')
            .attr('class', 'sankey-tooltip')
            .style('position', 'absolute')
            .style('background', isDark ? '#424242' : '#FFFFFF')
            .style('border', `1px solid ${isDark ? '#666' : '#ccc'}`)
            .style('border-radius', '4px')
            .style('padding', '8px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('opacity', 0)
            .style('color', textColor)
            .style('box-shadow', '0 2px 8px rgba(0,0,0,0.15)')

          tooltip.transition()
            .duration(200)
            .style('opacity', 1)

          tooltip.html(`
            <div><strong>${d.source.name} → ${d.target.name}</strong></div>
            <div>${formatCurrency(d.value)}</div>
          `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
        })
        .on('mouseout', function() {
          d3.select(this).attr('opacity', 0.6)
          d3.selectAll('.sankey-tooltip').remove()
        })

      // Create nodes
      const node = g.append('g')
        .selectAll('.node')
        .data(sankeyNodes)
        .enter()
        .append('g')
        .attr('class', 'node')

      // Node rectangles
      node.append('rect')
        .attr('x', d => d.x0)
        .attr('y', d => d.y0)
        .attr('height', d => d.y1 - d.y0)
        .attr('width', d => d.x1 - d.x0)
        .attr('fill', d => d.name === 'Total Expenses' ? nodeColor : colorScale(d.name))
        .attr('stroke', 'none')
        .attr('rx', 3)

      // Left-side labels (Total Expenses)
      g.selectAll('.source-label')
        .data(sankeyNodes.filter(d => d.name === 'Total Expenses'))
        .enter()
        .append('text')
        .attr('class', 'source-label')
        .attr('x', d => d.x0 - 10)
        .attr('y', d => (d.y0 + d.y1) / 2)
        .attr('dy', '0.35em')
        .attr('text-anchor', 'end')
        .attr('font-size', '14px')
        .attr('font-weight', '600')
        .attr('fill', textColor)
        .text(d => d.name)

      g.selectAll('.source-amount')
        .data(sankeyNodes.filter(d => d.name === 'Total Expenses'))
        .enter()
        .append('text')
        .attr('class', 'source-amount')
        .attr('x', d => d.x0 - 10)
        .attr('y', d => (d.y0 + d.y1) / 2 + 18)
        .attr('text-anchor', 'end')
        .attr('font-size', '12px')
        .attr('font-weight', '500')
        .attr('fill', nodeColor)
        .text(d => formatCurrency(d.value || 0))

      // Right-side labels (Categories)
      g.selectAll('.target-label')
        .data(sankeyNodes.filter(d => d.name !== 'Total Expenses'))
        .enter()
        .append('text')
        .attr('class', 'target-label')
        .attr('x', d => d.x1 + 10)
        .attr('y', d => (d.y0 + d.y1) / 2)
        .attr('dy', '0.35em')
        .attr('text-anchor', 'start')
        .attr('font-size', '13px')
        .attr('font-weight', '600')
        .attr('fill', textColor)
        .text(d => d.name.length > 20 ? d.name.substring(0, 17) + '...' : d.name)

      g.selectAll('.target-amount')
        .data(sankeyNodes.filter(d => d.name !== 'Total Expenses'))
        .enter()
        .append('text')
        .attr('class', 'target-amount')
        .attr('x', d => d.x1 + 10)
        .attr('y', d => (d.y0 + d.y1) / 2 + 16)
        .attr('text-anchor', 'start')
        .attr('font-size', '11px')
        .attr('font-weight', '500')
        .attr('fill', d => colorScale(d.name))
        .text(d => formatCurrency(d.value || 0))
    }

    // Watch for data changes
    watch(() => props.data, () => {
      nextTick(() => {
        createSankey()
      })
    }, { deep: true })

    // Watch for theme changes
    watch(() => theme.global.current.value.dark, () => {
      nextTick(() => {
        createSankey()
      })
    })

    onMounted(() => {
      nextTick(() => {
        createSankey()
      })

      // Handle window resize
      const handleResize = () => {
        createSankey()
      }
      window.addEventListener('resize', handleResize)

      // Cleanup
      return () => {
        window.removeEventListener('resize', handleResize)
      }
    })

    return {
      sankeyEl,
      sankeyContainer
    }
  }
}
</script>

<style scoped>
.sankey-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

svg {
  max-width: 100%;
  height: auto;
}

/* Ensure tooltips appear above everything */
:global(.sankey-tooltip) {
  z-index: 1000;
}
</style>