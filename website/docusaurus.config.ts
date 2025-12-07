import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'A Comprehensive Guide to Embodied Intelligence',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://asim04.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is '/<projectName>/'
  baseUrl: '/Humanoid-Robotics-Textbook/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'Asim04', // Usually your GitHub org/user name.
  projectName: 'Humanoid-Robotics-Textbook', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  markdown: {
    mermaid: true,
    mdx1Compat: {
      comments: true,
      admonitions: true,
      headingIds: true,
    },
    // Add configuration for broken markdown images
    hooks: {
      onBrokenMarkdownImages: 'warn', // Change from default 'throw' to 'warn'
    },
  },

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/Asim04/Humanoid-Robotics-Textbook',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          // Markdown and Remark plugins for KaTeX support
          remarkPlugins: [require('remark-math')],
          rehypePlugins: [require('rehype-katex')],
        },
        blog: false, // Disable blog for textbook
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    // Redirects
    [
      '@docusaurus/plugin-client-redirects',
      {
        redirects: [
          {
            to: '/docs/part-i-foundations/chapter-1',
            from: '/docs/intro',
          },
        ],
      },
    ],
    // Additional plugins for textbook features
    // Note: sitemap is already included in the classic preset
  ],

  themeConfig: {
    // Matomo analytics configuration
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI & Robotics',
      logo: {
        alt: 'Physical AI & Humanoid Robotics Textbook',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          to: '/docs/part-i-foundations/chapter-1',
          label: 'Chapters',
          position: 'left',
        },
        {
          to: '/docs/labs',
          label: 'Labs',
          position: 'left',
        },
        {
          to: '/docs/code-examples',
          label: 'Code',
          position: 'left',
        },
        {
          href: 'https://github.com/Asim04/Humanoid-Robotics-Textbook',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Textbook',
          items: [
            {
              label: 'Part I: Foundations',
              to: '/docs/part-i-foundations/chapter-1',
            },
            {
              label: 'Part II: ROS 2 Fundamentals',
              to: '/docs/part-ii-ros-fundamentals',
            },
            {
              label: 'Part III: Perception & Control',
              to: '/docs/part-iii-perception-control',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'Code Examples',
              to: '/docs/code-examples',
            },
            {
              label: 'Lab Exercises',
              to: '/docs/labs',
            },
            {
              label: 'Hardware Guide',
              to: '/docs/hardware-setup',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/Asim04/Humanoid-Robotics-Textbook',
            },
            {
              label: 'ROS Answers',
              href: 'https://answers.ros.org/',
            },
            {
              label: 'NVIDIA Developer',
              href: 'https://developer.nvidia.com/',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
