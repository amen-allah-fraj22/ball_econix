# backend/economic_platform/analytics/chart_configs.py

CHART_CONFIGURATIONS = {
    'global_inflation_trends': {
        'title': 'Global Inflation Trends Over Time',
        'type': 'line',  # Suggested chart type
        'data_source': 'api/analytics/inflation_trends/', # Example API endpoint
        'params': { # Potential parameters for fetching data
            'metrics': ['headline_consumer_price_inflation', 'food_consumer_price_inflation', 'energy_consumer_price_inflation'],
            'group_by': 'year',
            'aggregation': 'mean', # Default aggregation
        },
        'options': { # Chart.js options
            'responsive': True,
            'scales': {
                'y': {
                    'beginAtZero': False,
                    'title': {'display': True, 'text': 'Average Inflation Rate (%)'}
                },
                'x': {
                    'title': {'display': True, 'text': 'Year'}
                }
            },
            'plugins': {
                'legend': {'position': 'top'},
                'tooltip': {'mode': 'index', 'intersect': False}
            }
        }
    },
    'happiness_vs_inflation': {
        'title': 'Happiness Score vs. Headline Inflation',
        'type': 'scatter', # Suggested chart type
        'data_source': 'api/analytics/correlation_analysis/', # Example API endpoint or a dedicated one
        'params': {
            'x_axis': 'headline_consumer_price_inflation',
            'y_axis': 'happiness_score',
            'color_by': 'continent' # If API supports returning continent for coloring
        },
        'options': { # Chart.js options
            'responsive': True,
            'scales': {
                'x': {
                    'type': 'linear',
                    'position': 'bottom',
                    'title': {'display': True, 'text': 'Headline Inflation Rate (%)'}
                },
                'y': {
                    'title': {'display': True, 'text': 'Happiness Score'}
                }
            },
            'plugins': {
                'legend': {'display': True, 'position': 'top'}, # Show legend if color_by is used
                'tooltip': {
                    'callbacks': {
                        # Placeholder for a more detailed tooltip if needed
                        'label': "function(context) { return context.dataset.label + ': (' + context.parsed.x + ', ' + context.parsed.y + ')'; }"
                    }
                }
            }
        }
    },
    'pca_analysis': {
        'title': 'PCA of Economic Indicators',
        'type': 'scatter', # Typically for showing PC1 vs PC2
        # Data source might be a specific API endpoint that returns pre-calculated PCA results
        'data_source': 'api/analytics/pca_results/',
        'params': {
            'components': ['PC1', 'PC2'], # Which components to plot
        },
        'options': {
            'responsive': True,
            'scales': {
                'x': {'title': {'display': True, 'text': 'Principal Component 1'}},
                'y': {'title': {'display': True, 'text': 'Principal Component 2'}}
            },
            'plugins': {
                'tooltip': {
                    'callbacks': {
                         # Tooltip could show country name if data points represent countries
                        'label': "function(context) { return 'Country: (' + context.parsed.x + ', ' + context.parsed.y + ')'; }"
                    }
                }
            }
        },
        # Static data that would come from Jupyter output, as per instructions
        'explained_variance_ratio': [0.45, 0.25], # Example: PC1 explains 45%, PC2 explains 25%
        'components_loading': { # Example structure for factor loadings
            'PC1': {
                'gdp_per_capita': 0.85,
                'social_support': 0.70,
                'healthy_life_expectancy_at_birth': 0.75,
                'headline_consumer_price_inflation': -0.30
            },
            'PC2': {
                'freedom_to_make_life_choices': 0.60,
                'generosity': 0.40,
                'perceptions_of_corruption': -0.55,
                'headline_consumer_price_inflation': 0.20
            }
        },
        'insights': [
            "PC1 is strongly correlated with GDP, social support, and life expectancy.",
            "PC2 seems to capture aspects of freedom, generosity, and corruption perception.",
            "Inflation has a moderate negative loading on PC1."
        ]
    }
    # Further charts from the Jupyter notebook would be added here following similar structures.
}
