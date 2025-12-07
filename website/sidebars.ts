import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Introduction & Getting Started',
      items: [
        'intro',
        'course-overview',
        'hardware-requirements',
        'software-installation',
        'learning-path-navigator',
      ],
      link: {
        type: 'doc',
        id: 'intro',
      },
    },
    {
      type: 'category',
      label: 'Part I: Foundations (Weeks 1-2)',
      items: [
        'part-i-foundations/chapter-1',
        'part-i-foundations/chapter-2',
      ],
      link: {
        type: 'generated-index',
        title: 'Part I: Foundations',
        description: 'Weeks 1-2 - Building the foundation for Physical AI and Robotics',
        slug: '/part-i-foundations',
      },
    },
  ],
};

export default sidebars;
